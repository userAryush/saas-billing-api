import logging
from datetime import datetime, timezone as dt_timezone

from celery import shared_task
from django.db import transaction

from .models import ProcessedWebhookEvent
from billing.models import Subscription, Invoice, Plan

logger = logging.getLogger(__name__)

STRIPE_TO_LOCAL_STATUS = {
    'trialing': 'trialing',
    'active': 'active',
    'past_due': 'past_due',
    'unpaid': 'past_due',
    'canceled': 'cancelled',
    'incomplete': 'trialing',
    'incomplete_expired': 'cancelled',
}


def _to_datetime(unix_timestamp):
    if unix_timestamp is None:
        return None
    return datetime.fromtimestamp(unix_timestamp, tz=dt_timezone.utc)


def handle_invoice_paid(data):
    sub_id = data.get('subscription')
    if not sub_id:
        return

    subscription = Subscription.objects.get(stripe_subscription_id=sub_id)
    subscription.status = 'active'
    subscription.save()

    Invoice.objects.get_or_create(
        stripe_invoice_id=data['id'],
        defaults={
            'subscription': subscription,
            'amount': data.get('amount_paid', 0),
            'status': 'paid',
            'period_start': _to_datetime(data.get('period_start')),
            'period_end': _to_datetime(data.get('period_end')),
        },
    )


def handle_invoice_payment_failed(data):
    sub_id = data.get('subscription')
    if not sub_id:
        return

    subscription = Subscription.objects.get(stripe_subscription_id=sub_id)
    subscription.status = 'past_due'
    subscription.save()

    Invoice.objects.get_or_create(
        stripe_invoice_id=data['id'],
        defaults={
            'subscription': subscription,
            'amount': data.get('amount_due', 0),
            'status': 'open',
            'period_start': _to_datetime(data.get('period_start')),
            'period_end': _to_datetime(data.get('period_end')),
        },
    )


def handle_subscription_updated(data):
    subscription = Subscription.objects.get(stripe_subscription_id=data['id'])
    subscription.status = STRIPE_TO_LOCAL_STATUS.get(data.get('status'), subscription.status)
    subscription.cancel_at_period_end = data.get('cancel_at_period_end', False)
    subscription.save()


def handle_subscription_deleted(data):
    Subscription.objects.filter(stripe_subscription_id=data['id']).update(status='cancelled')


EVENT_HANDLERS = {
    'invoice.paid': handle_invoice_paid,
    'invoice.payment_failed': handle_invoice_payment_failed,
    'customer.subscription.updated': handle_subscription_updated,
    'customer.subscription.deleted': handle_subscription_deleted,
}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_stripe_event(self, stripe_event_id):
    event = ProcessedWebhookEvent.objects.get(stripe_event_id=stripe_event_id)

    if event.status == 'processed':
        return

    data = event.payload.get('data', {}).get('object', {})
    handler = EVENT_HANDLERS.get(event.event_type)

    try:
        with transaction.atomic():
            if handler:
                handler(data)
            event.status = 'processed'
            event.save(update_fields=['status'])
    except Exception as exc:
        event.status = 'failed'
        event.save(update_fields=['status'])
        logger.exception("Failed processing event %s", stripe_event_id)
        raise self.retry(exc=exc)
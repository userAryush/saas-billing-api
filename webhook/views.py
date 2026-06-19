import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import json
from .models import ProcessedWebhookEvent
from .task import process_stripe_event  

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeWebhookView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        payload = request.body  # raw bytes, not request.data
        sig_header = request.headers.get('Stripe-Signature')

        # 1 & 2. Verify signature; on any failure return 400.
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.STRIPE_WEBHOOK_SECRET,
            )
            event_dict = json.loads(str(event))
        except ValueError:
            # Malformed payload (couldn't even parse the JSON)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            # Payload parsed, but signature didn't match -> not really from Stripe
            return Response(status=status.HTTP_400_BAD_REQUEST)


        # get_or_create does the "check then insert" atomically, so two
        # near-simultaneous deliveries of the same event can't both pass.
        _, created = ProcessedWebhookEvent.objects.get_or_create(
            stripe_event_id=event['id'],
            defaults={
                'event_type': event['type'],
                'payload': event_dict,          # store the whole event dict
                'status': 'pending',
            },
        )

        if not created:
            # We've already seen this event -> ack so Stripe stops retrying.
            return Response(status=status.HTTP_200_OK)

        # 5. Hand off the actual work to Celery (keep the webhook fast).
        process_stripe_event.delay(event['id'])

        # 6. Acknowledge receipt.
        return Response(status=status.HTTP_200_OK)
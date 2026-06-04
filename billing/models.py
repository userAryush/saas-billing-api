from base.models import BaseModel
from django.db.models import CharField, DecimalField, BooleanField, DateTimeField, ForeignKey, OneToOneField,IntegerField
from tenants.models import Organisation
from django.db.models import PROTECT

# Create your models here.
class Plan(BaseModel):
    INTERVAL = [('month','Monthly'),('year','Yearly')]
    name = CharField(max_length=100)
    max_members = IntegerField()
    stripe_price_id = CharField(max_length=100, unique=True)
    amount = IntegerField()
    billing_interval = CharField(choices=INTERVAL, max_length=10)
    is_active = BooleanField(default=True)


class Subscription(BaseModel):
    STATUS = [('trialing','Trialing'),
              ('active','Active'),
              ('past_due','Past due'),
              ('cancelled','Cancelled')]
    org = OneToOneField(Organisation, on_delete=PROTECT)
    plan = ForeignKey(Plan, on_delete=PROTECT)
    status = CharField(choices=STATUS,max_length=10, default='trialing')
    stripe_subscription_id = CharField(max_length=100, unique=True, blank=True, null=True)
    current_period_start = DateTimeField()
    current_period_end = DateTimeField()
    cancel_at_period_end = BooleanField(default=False)

class Invoice(BaseModel):
    STATUS = [('open','Open'),
              ('paid','Paid'),
              ('void','Void'),
              ('uncollectible','Uncollectible')]
    subscription = ForeignKey(Subscription, on_delete=PROTECT, related_name='invoices')
    stripe_invoice_id = CharField(max_length=100, unique=True)

    amount = IntegerField()
    status = CharField(choices=STATUS, max_length=20)
    period_start = DateTimeField()
    period_end = DateTimeField()


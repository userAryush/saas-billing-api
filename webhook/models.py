from django.db.models import CharField, DateTimeField
from base.models import BaseModel
from django.db.models import JSONField

# Create your models here.
class ProcessedWebhookEvent(BaseModel):

    STATUS = [
    ('pending', 'Pending'),
    ('processed', 'Processed'),
    ('failed', 'Failed'),
    ]
    stripe_event_id = CharField(max_length=100, unique=True)
    event_type = CharField(max_length=100)
    processed_at = DateTimeField(auto_now_add=True)
    payload = JSONField()
    status = CharField(choices=STATUS, max_length=10, default='pending')
    
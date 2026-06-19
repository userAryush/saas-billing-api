import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saas_billing_api.settings')

app = Celery('saas_billing_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
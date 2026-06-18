from rest_framework import serializers
from .models import Plan, Subscription, Invoice


class PlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'amount', 'billing_interval', 'max_members', 'is_active']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'org', 'plan', 'status', 'current_period_start', 'current_period_end', 'cancel_at_period_end']
        read_only_fields = fields

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'stripe_invoice_id', 'amount', 'status', 'period_start', 'period_end', 'created_at']
        read_only_fields = fields

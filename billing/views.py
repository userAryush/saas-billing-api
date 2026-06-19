from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from .serializers import PlanListSerializer, InvoiceSerializer, SubscriptionSerializer
from .models import Plan, Subscription, Invoice
from accounts.models import User
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from tenants.views import get_current_organisation
from rest_framework.permissions import AllowAny


class PlanListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanListSerializer


def get_current_subscription(user):
    org = get_current_organisation(user)
    if org is None:
        return None
    return getattr(org, 'subscription', None)

class MySubscriptionView(RetrieveAPIView):
    serializer_class = SubscriptionSerializer

    def get_object(self):
        sub = get_current_subscription(self.request.user)
        if sub is None:
            raise NotFound("No subscription found.")
        return sub


class InvoiceListView(ListAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        sub = get_current_subscription(self.request.user)
        if sub is None:
            return Invoice.objects.none()
        return Invoice.objects.filter(subscription=sub)

class CreateSubscriptionView(CreateAPIView):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

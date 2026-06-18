from django.urls import path
from .views import PlanListView, MySubscriptionView, InvoiceListView, CreateSubscriptionView
urlpatterns = [
    path('plan-listing/', PlanListView.as_view(), name='plan_list'),
    path('my-subscription/', MySubscriptionView.as_view(), name='my_subs'),
    path('invoice-list/', InvoiceListView.as_view(), name='invoice_list'),
    path('create-subscription/', CreateSubscriptionView.as_view(), name='create_subscription'),
]

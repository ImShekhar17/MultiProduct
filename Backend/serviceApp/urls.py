from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/<uuid:product_id>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('subscriptions/list/', SubscriptionListAPIView.as_view(), name='user-subscriptions'),
    path('subscriptions/', UserSubscriptionListAPIView.as_view(), name='user-subscriptions'),
    path('subscriptions/trial/start/', StartTrialAPIView.as_view(), name='start-trial'),
    path('subscriptions/purchase/', PurchaseSubscriptionAPIView.as_view(), name='purchase-subscription'),
    path('subscriptions/<uuid:subscription_id>/cancel/', CancelSubscriptionAPIView.as_view(), name='cancel-subscription'),
    path('subscriptions/<uuid:subscription_id>/renew/', RenewSubscriptionAPIView.as_view(), name='renew-subscription'),

    path('invoice/create/', CreateInvoiceAPIView.as_view(), name='create-invoice'),
    path('payment/process/', ProcessPaymentAPIView.as_view(), name='process-payment'),
    path('invoices/', GetInvoicesAPIView.as_view(), name='get-invoices'),
    path('notifications/', GetNotificationsAPIView.as_view(), name='get-notifications'),
    path('notifications/<int:notification_id>/read/', MarkNotificationAsReadAPIView.as_view(), name='mark-notification-read'),
]




"""
For the all api in one api url work process
path('subscriptions/', SubscriptionAPIView.as_view(), name='subscription-management'),
path('subscriptions/<int:subscription_id>/', SubscriptionAPIView.as_view(), name='subscription-detail'),
**Usage examples:**
GET /subscriptions/ → Get available plans

POST /subscriptions/ with {"action": "purchase", "product": 1, "plan": 1}

POST /subscriptions/5/ with {"action": "cancel"}

POST /subscriptions/5/ with {"action": "renew"}
"""
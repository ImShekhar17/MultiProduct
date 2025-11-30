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
]
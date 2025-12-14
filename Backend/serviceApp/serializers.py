from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import (
    Product, SubscriptionPlan, UserSubscription, 
    Invoice, Transaction, Notification
)


class ProductSerializer(serializers.ModelSerializer):
    available_plans = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'base_price', 'is_active', 
                  'trial_duration', 'available_plans', 'created_at']
        read_only_fields = ['created_at']
    
    def get_available_plans(self, obj):
        plans = obj.plans.filter(is_trial=False)
        return SubscriptionPlanSerializer(plans, many=True).data


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'product', 'product_name', 'name', 'plan_type', 
                  'description', 'duration_days', 'price', 'discount', 
                  'final_price', 'is_trial']
        read_only_fields = ['final_price']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'product', 'product_name', 'plan', 'plan_name',
                  'start_date', 'end_date', 'status', 'auto_renew', 'days_remaining']
        read_only_fields = ['user', 'start_date', 'end_date', 'status']
    
    def get_days_remaining(self, obj):
        if obj.status in ['expired', 'cancelled']:
            return 0
        delta = obj.end_date - timezone.now().date()
        return max(0, delta.days)


class PurchaseSubscriptionSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    plan_id = serializers.UUIDField()
    auto_renew = serializers.BooleanField(default=False)
    
    def validate(self, data):
        product = Product.objects.filter(
            id=data['product_id'],
            is_active=True
        ).first()

        if not product:
            raise serializers.ValidationError("Product not found or inactive")

        plan = SubscriptionPlan.objects.filter(
            id=data['plan_id'],
            product=product,
            is_trial=False
        ).first()

        if not plan:
            raise serializers.ValidationError(
                "Invalid plan, trial plan, or plan does not belong to this product"
            )

        data['product'] = product
        data['plan'] = plan
        return data

class InvoiceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='user_subscription.product.name', read_only=True)
    user_email = serializers.CharField(source='user_subscription.user.email', read_only=True)
    plan_name = serializers.CharField(source='user_subscription.plan.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'user_subscription', 'product_name', 'plan_name', 'amount', 
                  'issued_date', 'due_date', 'is_paid', 'transaction_ref', 'user_email']
        read_only_fields = ['id', 'issued_date']


class TransactionSerializer(serializers.ModelSerializer):
    invoices = InvoiceSerializer(source='invoice_set', many=True, read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'total_amount', 'transaction_ref', 'status', 
                  'payment_method', 'created_at', 'invoices']
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    receiver_email = serializers.CharField(source='receiver.email', read_only=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'receiver', 'receiver_email', 'sender', 'sender_name', 'title', 
                  'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

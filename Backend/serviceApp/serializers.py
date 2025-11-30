from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import (
    Product, SubscriptionPlan, UserSubscription, 
    Invoice, Transaction, Notification, TranslatedText
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
        # Validate product exists and is active
        try:
            product = Product.objects.get(id=data['product_id'], is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive")
        
        # Validate plan exists and belongs to product
        try:
            plan = SubscriptionPlan.objects.get(
                id=data['plan_id'], 
                product=product,
                is_trial=False
            )
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid subscription plan for this product")
        
        data['product'] = product
        data['plan'] = plan
        return data



class InvoiceSerializer(serializers.ModelSerializer):
    user_subscription_details = UserSubscriptionSerializer(source='user_subscription', read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'user_subscription', 'user_subscription_details', 'amount', 'issued_date', 'due_date', 'is_paid', 'transaction_ref', 'created_at', 'updated_at']
        read_only_fields = ['id', 'issued_date', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'total_amount', 'transaction_ref', 'status', 'payment_method', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True, allow_null=True)

    class Meta:
        model = Notification
        fields = ['id', 'receiver', 'receiver_username', 'sender', 'sender_username', 'title', 'message', 'is_read', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
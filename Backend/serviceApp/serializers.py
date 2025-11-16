from rest_framework import serializers

from .models import (
    Product, SubscriptionPlan, UserSubscription, 
    Invoice, Transaction, Notification, TranslatedText
)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'base_price', 'product_schema', 'is_active', 'trial_duration', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'product', 'name', 'plan_type', 'description', 'duration_days', 'price', 'discount', 'final_price', 'is_trial', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_final_price(self, obj):
        return obj.final_price


class TranslatedTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslatedText
        fields = ['id', 'content_type', 'object_id', 'language_code', 'translated_text', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'product', 'product_name', 'plan', 'plan_name', 'start_date', 'end_date', 'status', 'auto_renew', 'created_at', 'updated_at']
        read_only_fields = ['id', 'start_date', 'created_at', 'updated_at']


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

from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from authApp.models import User,Common



# Product & Subscription Plans
class Product(Common):
   """
   Represents a product (e.g., CRM, Email Automation, Analytics).
   Each product can have its own subscription plans.
   """
   name = models.CharField(max_length=100,null=True,blank=True,unique=True)
   description = models.TextField(null=True, blank=True)
   base_price = models.DecimalField(max_digits=10, decimal_places=2)
   product_schema = models.JSONField(default=dict, null=True, blank=True)
   is_active = models.BooleanField(default=True)
   trial_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Trial duration in days")
   
   class Meta:
        permissions = [
            ("publish_product", "Can publish or unpublish product"),
            ("set_trial_duration", "Can set or modify trial duration"),
            ("view_product_sales", "Can view product sales analytics"),
        ]

   def __str__(self):
      return self.name


class SubscriptionPlan(Common):
   """
   Defines pricing and duration options for each product.
   Example: CRM - Monthly, Quarterly, Yearly.
   """
   WEEKLY = 'weekly'
   MONTHLY = 'monthly'
   QUARTERLY = 'quarterly'
   HALF_YEARLY = 'half_yearly'
   YEARLY = 'yearly'
   
   PLAN_TYPE_CHOICES = [
      (WEEKLY, 'Weekly'),
      (MONTHLY, 'Monthly'),
      (QUARTERLY, 'Quarterly'),
      (HALF_YEARLY, 'Half-Yearly'),
      (YEARLY, 'Yearly'),
   ]

   product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="plans")
   user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="subscription_plans")
   name = models.CharField(max_length=100)
   plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
   description = models.TextField(null=True, blank=True)
   duration_days = models.PositiveIntegerField(help_text="Duration in days")
   price = models.DecimalField(max_digits=10, decimal_places=2)
   discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
   is_trial = models.BooleanField(default=False)

   @property
   def final_price(self):
      return self.price - (self.price * (self.discount / 100)) if self.discount else self.price
      
   class Meta:
      unique_together = ('product', 'name', 'plan_type')
      permissions = [
         ("modify_discount", "Can modify discounts on plans"),
         ("create_promotional_plan", "Can create promotional or trial plans"),
         ("view_plan_performance", "Can view subscription plan performance"),
      ]

   def __str__(self):
      return f"{self.product.name} - {self.name}"


# User Subscription (Per Product)
class UserSubscription(Common):
   """
   Each subscription represents one user's access to a specific product
   under a specific plan. Independent per product.
   """
   TRIAL = 'trial'
   ACTIVE = 'active'
   EXPIRED = 'expired'
   CANCELLED = 'cancelled'
   
   STATUS_CHOICES = [
      (TRIAL, 'Trial'),
      (ACTIVE, 'Active'),
      (EXPIRED, 'Expired'),
      (CANCELLED, 'Cancelled'),
   ]

   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
   product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='subscriptions')
   plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
   start_date = models.DateField(auto_now_add=True)
   end_date = models.DateField()
   status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
   auto_renew = models.BooleanField(default=False)

   class Meta:
      unique_together = ('user', 'product', 'plan')
      indexes = [
          models.Index(fields=['status', 'end_date']),
      ]
      permissions = [
         ("activate_subscription", "Can manually activate a subscription"),
         ("cancel_subscription", "Can cancel a user's subscription"),
         ("renew_subscription", "Can renew expired subscriptions"),
         ("view_subscription_status", "Can view subscription status of users"),
      ]

   def __str__(self):
      return f"{self.user.username} - {self.product.name} ({self.plan.name})"


# Invoice
class Invoice(Common):
   """
   Invoice for a specific user subscription (per product).
   """
   user_subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='invoices')
   amount = models.DecimalField(max_digits=10, decimal_places=2)
   issued_date = models.DateField(auto_now_add=True)
   due_date = models.DateField()
   is_paid = models.BooleanField(default=False)
   transaction_ref = models.CharField(max_length=100, null=True, blank=True)
   
   class Meta:
        permissions = [
            ("mark_invoice_paid", "Can mark invoice as paid"),
            ("generate_invoice_pdf", "Can generate invoice PDF"),
            ("view_invoice_summary", "Can view all user invoices summary"),
        ]

   def __str__(self):
      return f"Invoice {self.id} - {self.user_subscription.user.username} ({self.user_subscription.product.name})"


# Transaction (Optional - Grouped Payment)
class Transaction(Common):
   """
   Handles payment transaction for one or multiple invoices.
   Useful if user pays for several products in one checkout.
   """
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
   total_amount = models.DecimalField(max_digits=10, decimal_places=2)
   transaction_ref = models.CharField(max_length=100, unique=True)
   status = models.CharField(max_length=20, default='success')
   payment_method = models.CharField(max_length=50, blank=True)
   
   class Meta:
        permissions = [
            ("process_refund", "Can process payment refunds"),
            ("view_transaction_history", "Can view all user transaction histories"),
            ("reconcile_payments", "Can reconcile multiple invoices into a transaction"),
        ]

   def __str__(self):
      return f"{self.transaction_ref} - {self.user.username}"


# Notification
class Notification(Common):
   """
   Stores user notifications for events such as renewals,
   payment confirmations, or trial expirations.
   """
   receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')
   sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications_sent')
   title = models.CharField(max_length=200,null=True,blank=True)
   message = models.TextField(max_length=2000)
   is_read = models.BooleanField(default=False)
   
   class Meta:
         verbose_name = "Notification"
         verbose_name_plural = "Notifications"
         permissions = [
                  ("send_system_notification", "Can send system-wide notifications"),
                  ("delete_user_notification", "Can delete user notifications"),
                  ("view_all_notifications", "Can view all system notifications"),
            ]      

   def __str__(self):
      return f"{self.receiver.username} - {self.title}"
  

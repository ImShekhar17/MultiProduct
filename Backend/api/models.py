from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission
import uuid


# Common Base Model
class Common(models.Model):
    """Base abstract model for all tables"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Role System (Role + UserRole)
class Role(Common):
   """
   Defines system roles such as Admin, Registered, Subscriber, etc.
   """
   name = models.CharField(max_length=100, unique=True)
   description = models.TextField(blank=True)
   permissions = models.ManyToManyField(Permission, blank=True)
   group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
   
   
   class Meta:
        permissions = [
            ("assign_role", "Can assign roles to users"),
            ("manage_permissions", "Can manage role permissions"),
            ("view_role_hierarchy", "Can view hierarchical role structure"),
        ]

   def __str__(self):
      return self.name


class UserRole(Common):
   """
   Bridge between User and Role.
   Supports users without subscriptions (Registered, Guest, etc.).
   """
   STATUS_CHOICES = [
      ('registered', 'Registered (no subscription)'),
      ('trial', 'Trial'),
      ('active', 'Active Subscriber'),
      ('expired', 'Expired Subscriber'),
      ('guest', 'Guest User'),
   ]

   user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_roles')
   role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='assigned_users')
   status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='registered')
   assigned_date = models.DateTimeField(auto_now_add=True)
   expires_at = models.DateTimeField(null=True, blank=True)

   class Meta:
        unique_together = ('user', 'role')
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        permissions = [
            ("assign_user_role", "Can assign user roles"),
            ("revoke_user_role", "Can revoke user roles"),
            ("view_user_roles", "Can view all user role assignments"),
        ]

   def __str__(self):
      return f"{self.user.username} → {self.role.name} ({self.status})"


# User Model
class User(AbstractUser,Common):
   """
   Custom user model supporting role assignment and subscriptions.
   """
   username = models.CharField(max_length=150, unique=True)
   first_name = models.CharField(max_length=30)
   last_name = models.CharField(max_length=30, blank=True)
   email = models.EmailField(unique=True)
   phone_number = models.CharField(max_length=15, unique=True)
   date_of_birth = models.DateField(null=True, blank=True)
   is_active = models.BooleanField(default=True)
   is_staff = models.BooleanField(default=False)
   role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
   gender = models.CharField(max_length=10, blank=True)
   address = models.JSONField(null=True, blank=True)
   notifications = models.JSONField(null=True, blank=True)
   
   class Meta:
      permissions = [
               ("deactivate_user", "Can deactivate user accounts"),
               ("reset_user_password", "Can reset passwords for other users"),
               ("view_user_activity", "Can view user activity or login history"),
         ]

   def __str__(self):
      return self.username


# Product & Subscription Plans
class Product(Common):
   """
   Represents a product (e.g., CRM, Email Automation, Analytics).
   Each product can have its own subscription plans.
   """
   name = models.CharField(max_length=100,null=True,blank=True, unique=True,index=True)
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
   PLAN_TYPE_CHOICES = [
      ('weekly', 'Weekly'),
      ('monthly', 'Monthly'),
      ('quarterly', 'Quarterly'),
      ('half_yearly', 'Half-Yearly'),
      ('yearly', 'Yearly'),
   ]

   product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="plans")
   name = models.CharField(max_length=100)
   plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
   description = models.TextField(blank=True)
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

from django.db import models
from django.conf import settings

class TranslatedText(models.Model):
    original_text = models.TextField()
    original_language = models.CharField(max_length=10)
    translations = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.original_text[:50]}... ({self.original_language})"

    def get_translation(self, language_code):
        return self.translations.get(language_code)

# User Subscription (Per Product)
class UserSubscription(Common):
   """
   Each subscription represents one user's access to a specific product
   under a specific plan. Independent per product.
   """
   STATUS_CHOICES = [
      ('trial', 'Trial'),
      ('active', 'Active'),
      ('expired', 'Expired'),
      ('cancelled', 'Cancelled'),
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
   

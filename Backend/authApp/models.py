from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid



# Common Base Model
class Common(models.Model):
    """Base abstract model for all tables"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        

# User Model
class User(AbstractUser,Common):
   """
   Custom user model supporting role assignment and subscriptions.
   """
   username = models.CharField(max_length=150, unique=True)
   first_name = models.CharField(max_length=30,null=True,blank=True)
   last_name = models.CharField(max_length=30, null=True, blank=True)
   email = models.EmailField(unique=True, null=True, blank=True)
   phone_number = models.CharField(max_length=15, unique=True,null=True, blank=True)
   date_of_birth = models.DateField(null=True, blank=True)
   is_active = models.BooleanField(default=True)
   is_staff = models.BooleanField(default=False)
   role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)
   gender = models.CharField(max_length=10, null=True, blank=True)
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

   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
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


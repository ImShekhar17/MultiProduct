from django.db import models
import uuid
from django.contrib.auth.models import Group

class common(models.Model):
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
      abstract = True

class user(common):
   username = models.CharField(max_length=150, unique=True)
   first_name = models.CharField(max_length=30)
   middle_name = models.CharField(max_length=30, null=True, blank=True)
   last_name = models.CharField(max_length=30, null=True, blank=True)
   email = models.EmailField(unique=True)
   phone_number = models.CharField(max_length=15, unique=True)
   date_of_birth = models.DateField(null=True, blank=True)
   is_active = models.BooleanField(default=True)
   is_staff = models.BooleanField(default=False)
   role = models.ForeignKey('role', on_delete=models.SET_NULL, null=True, blank=True)
   landline_number = models.CharField(max_length=15, null=True, blank=True)
   gender = models.CharField(max_length=10, null=True, blank=True)
   address1 = models.CharField(max_length=255, null=True, blank=True)
   address2 = models.CharField(max_length=255, null=True, blank=True)
   city = models.CharField(max_length=100, null=True, blank=True)
   state = models.CharField(max_length=100, null=True, blank=True)
   country = models.CharField(max_length=100, null=True, blank=True)
   pin_code = models.CharField(max_length=20, null=True, blank=True)
   designation_title = models.CharField(max_length=100, null=True, blank=True)
   subscription_plan = models.ForeignKey('user_subscription', on_delete=models.SET_NULL, null=True, blank=True)
   notification = models.JSONField(null=True, blank=True)

   def __str__(self):
      return f"{self.id}-{self.username}"
   
class role(common):
   name = models.CharField(max_length=100, unique=True)
   description = models.TextField(null=True, blank=True)
   group = models.ForeignKey(Group, on_delete=models.SET_NULL)
   def __str__(self):
      return f"{self.id}-{self.name}"

class subscription_plan(common):
   name = models.CharField(max_length=100, unique=True)
   description = models.TextField(null=True, blank=True)
   price = models.DecimalField(max_digits=10, decimal_places=2)
   products = models.ManyToManyField('product', blank=True)
   duration = models.IntegerField(help_text="Duration in days")
   discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

   def __str__(self):
      return f"{self.id}-{self.name}"
   
class user_subscription(common):
   user = models.ForeignKey(user, on_delete=models.CASCADE)
   subscription_plan = models.ForeignKey(subscription_plan, on_delete=models.CASCADE)
   start_date = models.DateField()
   end_date = models.DateField()
   trial_period = models.BooleanField(default=False)
   auto_renew = models.BooleanField(default=False)

   def __str__(self):
      return f"{self.id}-{self.user.username}-{self.subscription_plan.name}"

class product(common):
   name = models.CharField(max_length=100, unique=True)
   description = models.TextField(null=True, blank=True)
   price = models.DecimalField(max_digits=10, decimal_places=2)
   discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
   final_price = models.DecimalField(max_digits=10, decimal_places=2)
   trial_duration = models.IntegerField(help_text="Trial duration in days", null=True, blank=True)

   def __str__(self):
      return f"{self.id}-{self.name}"

class trial(common):
   user = models.ForeignKey(user, on_delete=models.CASCADE)
   product = models.ForeignKey(product, on_delete=models.CASCADE)
   duration = models.IntegerField(help_text="Duration in days")
   is_active = models.BooleanField(default=True)

   def __str__(self):
      return f"{self.id}-{self.user.username}-{self.product.name}"
   
class notification(common):
   user = models.ForeignKey(user, on_delete=models.CASCADE)
   sender = models.ForeignKey(user, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
   title = models.CharField(max_length=200)
   message = models.TextField()
   is_read = models.BooleanField(default=False)

   def __str__(self):
      return f"{self.id}-{self.user.username}-{self.title}"

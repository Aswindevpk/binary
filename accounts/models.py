from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from datetime import timedelta

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    about = models.TextField(blank=True)
    otp = models.CharField(max_length=6,null=True,blank=True)
    otp_gen_time = models.DateTimeField(null=True,blank=True)
    is_verified = models.BooleanField(default=False,null=True,blank=True)

class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True

class PasswordReset(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    gen_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Password reset for {self.user.username}"

class SubscriptionPlan(BaseModel):
    name = models.CharField(max_length=50, unique=True,null=True)
    desc = models.CharField(max_length=50, unique=True,null=True)
    benefits = models.JSONField(null=True)
    duration_days = models.PositiveIntegerField(blank=True,null=True)  # Duration of the subscription in days
    price = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)  # Price of the subscription

    def __str__(self):
        return self.name

class PremiumSubscription(BaseModel):
    user = models.OneToOneField(CustomUser, related_name='premium_subscription', on_delete=models.CASCADE,null=True)
    subscription_plan = models.ForeignKey(SubscriptionPlan, related_name='subscriptions', on_delete=models.CASCADE,null=True)
    subscription_start = models.DateTimeField(auto_now_add=True,blank=True)
    subscription_end = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.subscription_plan.name} Subscription for {self.user}"

    def save(self, *args, **kwargs):
        if not self.subscription_end:
            self.subscription_end = self.subscription_start + timedelta(days=self.subscription_plan.duration_days)
        super().save(*args, **kwargs)

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment: {self.user.username} - {self.amount}"
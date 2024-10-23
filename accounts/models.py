from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
import random

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    about = models.TextField(max_length=160,blank=True)
    otp = models.CharField(max_length=6,null=True,blank=True)
    #time otp generated for verification purpose
    otp_created_at = models.DateTimeField(null=True,blank=True)
    #is email verified
    is_verified = models.BooleanField(default=False,null=True,blank=True)
    img = models.ImageField(upload_to='profile_images/',null=True,blank=True)
    pronouns = models.CharField(max_length=10,blank=True)
    name = models.CharField(max_length=10,blank=True)

    def is_otp_expired(self):
            time_diff = timezone.now() - self.otp_created_at
            print(time_diff)
            #return false if 5 minutes have passed
            if time_diff < timedelta(minutes=5):
                return False
            return True

    def generate_otp(self):
        """ Genarate a random 6-digit OTP"""
        self.otp = str(random.randint(100000,999999))
        self.otp_created_at = timezone.now()

        return True

    def regenarate_otp(self):
        """Regenarate OTP if 5 minutes have passed since the last OTP genaration"""
        if self.otp_created_at:

            if not self.is_otp_expired():
                return False
            
            return self.generate_otp()
        
    def verify_otp(self,otp):
        """
        Verify the provided otp
        """
        if self.otp is None and self.otp_created_at is None:
            return False
        
        if otp != self.otp:
            return False
        
        if self.is_otp_expired():
            return False
        
        return True
        
class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True

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
        return f"{self.subscription_plan} Subscription for {self.user}"

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
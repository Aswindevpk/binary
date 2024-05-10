from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    otp = models.CharField(max_length=6,null=True,blank=True)
    otp_gen_time = models.DateTimeField(null=True,blank=True)
    is_verified = models.BooleanField(default=False,null=True,blank=True)
    is_creator = models.BooleanField(default=False,null=True,blank=True)

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

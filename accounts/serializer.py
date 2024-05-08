from rest_framework import serializers
from django.contrib.auth.models import User
from .models import NormalUser
from random import randint
from .utils import send_otp_email
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        if data['username']:
            if User.objects.filter(username=data['username']).exists():
                raise serializers.ValidationError("username is taken")
            if len(data['username']) < 3:
                raise serializers.ValidationError("username should be atleast 3 characters")
        if data['email']:
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError("email is taken")
            
        validate_password(data['password'])
            
        return data
    
    def create(self, data):
        # creating main user 
        user = User.objects.create(username=data['username'],email=data['email'])
        user.set_password(data['password'])
        user.save()
        #genarate otp
        otp = randint(1000,9999)
        #otp genarated time
        now = timezone.now()
        normal_user = NormalUser.objects.create(user=user,otp=str(otp),otp_gen_time=now)
        normal_user.save()
        # senting the created otp to user email 
        # send_otp_email(email=data['email'],otp=otp)
        return data
    
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

class GenarateOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


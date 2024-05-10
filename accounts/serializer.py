from rest_framework import serializers
from accounts.models import CustomUser
from random import randint
from .utils import send_otp_email
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    is_creator = serializers.BooleanField()

    def validate(self, data):
        if data['username']:
            if CustomUser.objects.filter(username=data['username']).exists():
                raise serializers.ValidationError("username is taken")
            if len(data['username']) < 3:
                raise serializers.ValidationError("username should be atleast 3 characters")
        if data['email']:
            if CustomUser.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError("email is taken")
            
        validate_password(data['password'])
            
        return data
    
    def create(self, data):
        # creating main user 
        user = CustomUser.objects.create(username=data['username'],email=data['email'])
        user.set_password(data['password'])
        #genarate otp
        otp = randint(1000,9999)
        #otp genarated time
        now = timezone.now()
        user.otp = otp
        user.otp_gen_time = now
        if data['is_creator']:
            user.is_creator = True
        user.is_creator = False
        user.save()
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

class ResetPassSerializer(serializers.Serializer):
    password = serializers.CharField()

    def validate(self, data):  
        validate_password(data['password'])
        return data


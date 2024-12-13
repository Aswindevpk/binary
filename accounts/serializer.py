from rest_framework import serializers
from accounts.models import CustomUser
from .utils import send_otp_email
from django.contrib.auth.password_validation import validate_password
from accounts.models import Payment


"""
serializers for authenticatin and related
"""

class RegisterSerializer(serializers.ModelSerializer):
    #adding validator to pass
    password = serializers.CharField(write_only=True,validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'confirm_password')

    def validate(self, data):
        #username validations
        username = data.get('username', None)
        if username:
            if CustomUser.objects.filter(username=username).exists():
                raise serializers.ValidationError({"username":"Entered username is already taken by another user"})
            if len(username) < 3:
                raise serializers.ValidationError({"username":"username should be atleast 3 characters"})
        
        #validate password equality
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        #validate email
        email = data.get('email', None)
        if email:
            if CustomUser.objects.filter(email=email).exists():
                raise serializers.ValidationError({"email":"Entered email is already taken by another user"})

        return data
    
    
    def create(self, validated_data):
        #creating user
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'])
        user.set_password(validated_data['password'])

        #generate otp
        user.generate_otp()
        user.save()

        # senting the created otp to user email 
        send_otp_email(email=validated_data['email'],otp=user.otp)
        return user
    
from django.contrib.auth import authenticate
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True,required=True,validators=[validate_password])

    def validate(self, attrs):
        #username validation
        username = attrs.get('username', None)
        password = attrs.get('password', None)
        if username:
            if len(username) < 3:
                raise serializers.ValidationError({"username":"username should be atleast 3 characters"})
        
        #authenticate user
        user = authenticate(username=username,password=password)

        #no user exist
        if user is None:
            raise serializers.ValidationError(({"username":"Invalid username or password."}))

        #adding to attrs to access in the view
        attrs['user'] = user
        attrs['is_verified'] = user.is_verified

        return attrs
    
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            token = attrs.get('refresh', None)
            RefreshToken(token)
        except TokenError:
            raise serializers.ValidationError({"refresh":"Invalid refresh token"})
        
        return attrs
    
class VerifyOtpSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        username = attrs.get('username')
        otp = attrs.get('otp')

        if otp:
            if len(otp) != 6 :
                raise serializers.ValidationError({"otp":"otp should be 6 digits."})
        
        try:
            #status variable for verification
            is_verified = False
            user = CustomUser.objects.get(username=username)

            if user.verify_otp(otp=otp):
                #make the account verified in the database
                user.is_verified = True
                user.save()
                is_verified = True
            else:
                raise serializers.ValidationError(({"otp":"otp not verified ! Try again!"}))

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"error":"No Account Exists with this username."})

        attrs['is_verified'] = is_verified
        return attrs

class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email',None)
        try:
            user = CustomUser.objects.get(email=email)
            #exists but already verified
            if user and user.is_verified:
                raise serializers.ValidationError({"email":"You Email is already verified!"})
            #only generate after 5 min
            if not user.regenarate_otp(): #return true or false
                raise serializers.ValidationError({"error":"Already Existing OTP not expired.try after some time"})
            
            user.save()
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"email":"No Account Exists with this email"})

        return attrs

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        """
        validate that the email exists
        """
        try:
            email = attrs.get('email',None)
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(({"email":"No Account Exists with this email"}))
        return attrs
    
    def save(self, **kwargs):
        """
        Genarate a password reset token and sent it via email
        """
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)

        
        # Generate the token and user ID (uid)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build the password reset URL for the frontend app
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        # Send password reset email
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

from django.utils.http import urlsafe_base64_decode
class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True,validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True,required=True)

    def validate(self, attrs):
        """
        Validate the token and user ID.
        """
        print(attrs)
        #validate password equality
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        try:
            #Decode username from uid64
            uid = urlsafe_base64_decode(attrs['uidb64']).decode()
            user = CustomUser.objects.get(pk=uid)
        except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError({"error":"Invalid user or token."})

        # Validate the token
        if not default_token_generator.check_token(user,attrs['token']):
            raise serializers.ValidationError({"error":"Invalid or expired token."})
        
        return attrs
    
    def save(self, **kwargs):
        """
        Save the new password for the user.
        """
        uid = urlsafe_base64_decode(self.validated_data['uidb64']).decode()
        user = CustomUser.objects.get(pk=uid)
        user.set_password(self.validated_data['password'])
        user.save()


"""
For Profile updation
"""
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id','username','name','about','email','img','pronouns')

from home.models import Follow
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['follower','followed']
        extra_kwargs = {
            'follower':{'read_only':True}
        }





# for razor pay 
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SubscriptionPlan,PremiumSubscription
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .permissions import IsUnauthenticated
import razorpay
from django.conf import settings
from django.db import transaction

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


"""
    Authentication and related views
"""

class RegisterView(APIView):
    #allow only unauthenticated user
    permission_classes = [IsUnauthenticated]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    #allow only unauthenticated user
    permission_classes = [IsUnauthenticated]

    def post(self,request):
        data = request.data
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            is_verified = serializer.validated_data['is_verified']
            if is_verified:
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                refresh['username'] = user.username
                return Response({
                            'refresh': str(refresh),
                            'access': str(refresh.access_token)
                            }, status.HTTP_200_OK)
            return Response({
                "error":"Email not verified !",
                }, status.HTTP_401_UNAUTHORIZED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = RefreshToken(serializer.validated_data['refresh'])
                #blacklist the token
                token.blacklist()

                return Response({
                "message": "Successfully logged out."
                }, status=status.HTTP_205_RESET_CONTENT)
            
            except Exception as e:
                return Response({
                    'error':e
                },status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOtpView(APIView):
    #allow only unauthenticated user
    permission_classes = [IsUnauthenticated]

    def post(self, request):
        data = request.data 
        serializer = ResendOtpSerializer(data=data)
        if serializer.is_valid():
            return Response({
                'message':'new otp send successfully'
            }, status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOtpView(APIView):
    #allow only unauthenticated user
    permission_classes = [IsUnauthenticated]

    def post(self,request):
        try:
            serializer = VerifyOtpSerializer(data=request.data)
            if serializer.is_valid():
                is_verified = serializer.validated_data['is_verified']

                if is_verified:
                    return Response({
                        "message": "Otp verified Successfully."
                    }, status=status.HTTP_200_OK)
            return Response({
                'message':serializer.errors
            }, status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status':False, 'message':str(e)}, status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    #allow only unauthenticated user
    permission_classes = [IsUnauthenticated]

    def post(self,request):
        data = request.data
        serializer = PasswordResetRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "If the email exists, a reset link has been sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    #allow only unauthenticated user
    permission_classes = [IsUnauthenticated]

    def post(self, request):
        data = request.data
        serializer = PasswordResetConfirmSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
            
"""
    user data editing realted views
"""
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the currently logged-in user
        return self.request.user


"""
    User Follow related views
"""
from home.models import Follow
class FollowUserView(generics.CreateAPIView):
    serializer_class = FollowSerializer

    def create(self, request, *args, **kwargs):
        followed_user_id = self.kwargs['uid']
        try:
            followed_user = CustomUser.objects.get(id=followed_user_id)
        except CustomUser.DoesNotExist:
            return Response({"error":"user not found."},status=status.HTTP_404_NOT_FOUND)
        
        follow_relation ,created = Follow.objects.get_or_create(
            follower=request.user,
            followed=followed_user
        )

        if created:
            return Response({"message":"You are now following this user."},status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"You are already following this user."},status=status.HTTP_200_OK)
        
#unfollow a user
class UnfollowUserView(generics.DestroyAPIView):
    serializer_class = FollowSerializer

    def delete(self, request, *args, **kwargs):
        followed_user_id = self.kwargs['uid']
        try:
            followed_user = CustomUser.objects.get(id=followed_user_id)
        except CustomUser.DoesNotExist:
            return Response({"error":"user not found."},status=status.HTTP_404_NOT_FOUND)
        
        try:
            follow_relation = Follow.objects.get(
                follower=request.user,
                followed=followed_user
            )
            follow_relation.delete()
            return Response({"message":"You have Unfollowed this user."},status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({"message":"You are not following this user."},status=status.HTTP_400_BAD_REQUEST)
       
class UserFollowStatsView(APIView):

    def get(self,request,*args,**kwargs):
        user_id = kwargs.get('uid')
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
             return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        #count the number of followers
        followers_count = Follow.objects.filter(followed=user).count()

        #count the number of following
        following_count = Follow.objects.filter(follower=user).count()

        return Response({
            "user_id": user_id,
            "followers_count": followers_count,
            "following_count": following_count
        })





class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        currency = 'INR'
        payment = Payment.objects.create(user=request.user, amount=amount)
        
        razorpay_order = client.order.create(dict(amount=int(amount)*100, currency=currency, payment_capture='1'))
        
        payment.razorpay_order_id = razorpay_order['id']
        payment.save()
        
        return Response({
            'order_id': razorpay_order['id'],
            'amount': amount,
            'currency': currency,
            'key': settings.RAZORPAY_KEY_ID,
            'name': "Your Blog",
            'description': "Blog Subscription",
        }, status=status.HTTP_201_CREATED)

class VerifyPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return Response({'status': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            with transaction.atomic():
                client.utility.verify_payment_signature(params_dict)
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.is_paid = True
                payment.save()
                
                # Creating premium subscription for the user
                plan = SubscriptionPlan.objects.get(price=payment.amount)
                current_datetime = timezone.now()

                new_plan = PremiumSubscription.objects.create(
                    subscription_plan=plan,
                    user=payment.user,
                    subscription_end=current_datetime + timedelta(days=plan.duration_days)
                )
                
                return Response({'status': 'Payment successful'}, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError as e:
            return Response({'status': 'Payment verification failed', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'An error occurred', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)












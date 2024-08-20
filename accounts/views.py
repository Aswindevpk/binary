from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PasswordReset, CustomUser,SubscriptionPlan,PremiumSubscription
from django.utils import timezone
from .utils import generate_token, send_password_reset_email
from datetime import timedelta
from random import randint
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


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
            client.utility.verify_payment_signature(params_dict)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.is_paid = True
            payment.save()
            # creating premium subsciption for user 
            plan = SubscriptionPlan.objects.get(price=payment.amount)
            current_datetime = timezone.now()

            new_plan = PremiumSubscription.objects.create(
                subscription_plan=plan,
                user=payment.user,
                subscription_end=current_datetime + timedelta(days=plan.duration_days)
            )
            return Response({'status': 'Payment successful'}, status=status.HTTP_200_OK)
        except:
            return Response({'status': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)

# authentication and related 

class RegisterUser(APIView):
    def post(self,request):
        try:
            data = request.data 
            serializer = RegisterSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    'status':False,
                    'message':serializer.errors
                    }, status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({'status':True, 'message':'user created'}, status.HTTP_201_CREATED)
    
        except:
            return Response({'status':False, 'message':"error occured"}, status.HTTP_400_BAD_REQUEST)

class VerifyOTPUser(APIView):
    def post(self,request):
        try:
            data = request.data
            print(data)
            serializer = OTPVerifySerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    'status':False,
                    'message':serializer.errors
                    }, status.HTTP_400_BAD_REQUEST)
            else:
                user = CustomUser.objects.get(email=data['email'])
                if not user:
                        return Response({
                        'status':False,
                        'message':'no user found'
                        }, status.HTTP_404_NOT_FOUND)
                
                if user.is_verified:
                        return Response({
                        'status':False,
                        'message':'email already verified'
                        }, status.HTTP_406_NOT_ACCEPTABLE)
                
                #time of join of the user
                created = user.otp_gen_time
                #current time
                now = timezone.now() 
                #time difference
                time_difference = now - created
                #time difference should not be greater than 5 min
                if time_difference < timedelta(minutes=5):
                    if data['otp'] == user.otp:
                        user.is_verified = True
                        user.save()
                        return Response({
                        'status':True,
                        'message':'email verified'
                        }, status.HTTP_202_ACCEPTED)
                    else:

                        return Response({
                        'status':False,
                        'message':'otp incorrect'
                        }, status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    return Response({
                    'status':False,
                    'message':'otp timeout'
                    }, status.HTTP_406_NOT_ACCEPTABLE)

        except Exception as e:
            return Response({'status':False, 'message':str(e)}, status.HTTP_400_BAD_REQUEST)

class GenarateOTPUser(APIView):
    def post(self, request):
        try:
            data = request.data 
            serializer = GenarateOTPSerializer(data=data)
            if not serializer.is_valid():
                    return Response({
                        'status':False,
                        'message':serializer.errors
                        }, status.HTTP_400_BAD_REQUEST)
            
            user = CustomUser.objects.get(email=data['email'])

            if user.is_verified:
                return Response({
                'status':False,
                'message':'email already verified'
                }, status.HTTP_406_NOT_ACCEPTABLE)
                
            #time of join of the user
            created = user.otp_gen_time
            #current time
            now = timezone.now() 
            #time difference
            time_difference = now - created
            #time difference should not be greater than 5 min

            if time_difference > timedelta(minutes=5):
                #change otp and time
                otp = randint(1000,9999) 
                user.otp = otp
                user.otp_gen_time = timezone.now()
                user.save()
                #sent new email
                #send_otp_email(email=data['email'],otp=otp)
                return Response({
                    'status':True,
                    'message':'new otp created successfully'
                }, status.HTTP_201_CREATED)
            else:
                return Response({
                    'status':False,
                    'message':'existing otp not expired'
                }, status.HTTP_406_NOT_ACCEPTABLE)
            
        except:
            return Response({
                'status':False,
                'message':serializer.errors
                }, status.HTTP_400_BAD_REQUEST)

class LoginUser(APIView):
    def post(self,request):
        data = request.data 
        serializer = LoginSerializer(data= data)
        if not serializer.is_valid():
            return Response({
                'status':False,
                'message':serializer.errors,
                'verified':True
                }, status.HTTP_400_BAD_REQUEST)
        
        user= authenticate(username=serializer.data['username'],password=serializer.data['password'])

        if not user :
            return Response({
                'status':False,
                'message':"Incorrect username or password.",
                'verified':True
                }, status.HTTP_401_UNAUTHORIZED)
        
        user = CustomUser.objects.get(username=data['username'])

        if not user.is_verified:
            return Response({
                'status':False,
                'message':"email not verified",
                'verified':False,
                'email':user.email
            }, status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        
        refresh['username'] = user.username
        return Response({'status':True, 
                         'message':'user login',
                         'refresh': str(refresh),
                          'access': str(refresh.access_token)
                         }, status.HTTP_200_OK)

class LogoutUser(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = LogoutSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                'status':False,
                'message':serializer.errors
                }, status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            return Response({
                'status':True,
                'message':"Logged out"
                },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status':False,
                'message':e
            },status=status.HTTP_400_BAD_REQUEST)

class ForgotPassUser(APIView):
    def post(self,request):
        data = request.data
        serializer = ForgotPassSerializer(data=data)
        if not serializer.is_valid():
            return Response({
            'status':False,
            'message':serializer.errors
            }, status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(email=serializer.data['email']).first()

        if not user:
            return Response({
            'status':False,
            'message':f"Account with email '{serializer.data['email']}' not found."
            }, status.HTTP_404_NOT_FOUND)
        
        reset_user = PasswordReset.objects.filter(user=user).first()
        if reset_user:
            return Response({
            'status':False,
            'message':"link already sent to email"
            }, status.HTTP_200_OK)
        
        token = generate_token()
        PasswordReset.objects.create(user=user,token=token)
        # send_password_reset_email(user.email, token)
        reset_url = reverse('user_forgot_pass_confirm', kwargs={'token': token})
        reset_link = request.build_absolute_uri(reset_url)
        return Response({
            'status':True,
            "message":"link sent to email"
        },status.HTTP_200_OK)

class ForgotPassConfirmUser(APIView):
    def post(self, request):
        data = request.data
        serializer = ForgotPassConfirmSerializer(data=data)
        if not serializer.is_valid():
            return Response({
            'status':False,
            'message':serializer.errors
            }, status.HTTP_400_BAD_REQUEST)
        
        token = serializer.data['token']
        reset_token = PasswordReset.objects.filter(token=token).first()
        if not reset_token:
            return Response({
            'status':False,
            "message":"reset_link invalid"
            },status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'status':True,
            "message":"reset your password"
        },status.HTTP_200_OK)
    
class ResetPassUser(APIView):
    def post(self, request):
        data = request.data
        serializer = ResetPassSerializer(data=data)
        if not serializer.is_valid():
            return Response({
            'status':False,
            "message":serializer.errors
        },status.HTTP_400_BAD_REQUEST)
        token = serializer.data['token']
        if not token:
            return Response({
            'status':False,
            "message":"token invalid"
            },status.HTTP_200_OK)
        try:
            reset_token = PasswordReset.objects.filter(token=token).first()
            if not reset_token:
                return Response({
                'status':False,
                "message":"token invalid"
                },status.HTTP_200_OK)
            user = CustomUser.objects.filter(id=reset_token.user.id).first()
            
            user.set_password(serializer.data["password"])
            user.save()
            reset_token.delete()
            return Response({
                'status':True,
                "message":"password reseted"
            },status.HTTP_200_OK)
        except:
            return Response({
            'status':False,
            "message":"token error"
            },status.HTTP_400_BAD_REQUEST)




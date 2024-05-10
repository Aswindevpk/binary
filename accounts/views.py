from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PasswordReset, CustomUser
from django.utils import timezone
from .utils import generate_token, send_password_reset_email
from datetime import timedelta
from random import randint
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse


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

        except:
            return Response({'status':False, 'message':serializer.errors}, status.HTTP_400_BAD_REQUEST)

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
                'message':serializer.errors
                }, status.HTTP_400_BAD_REQUEST)
        user= authenticate(username=serializer.data['username'],password=serializer.data['password'])
        if not user :
            return Response({
                'status':False,
                'message':"invalid credentials"
                }, status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.get(username=data['username'])

        if not user.is_verified:
            return Response({
                'status':False,
                'message':"email not verified"
            }, status.HTTP_400_BAD_REQUEST)


        refresh = RefreshToken.for_user(user)
        return Response({'status':True, 
                         'message':'user login',
                         'refresh': str(refresh),
                          'access': str(refresh.access_token),
                         }, status.HTTP_201_CREATED)

class LogoutUser(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ForgotPassUser(APIView):
    def post(self,request):
        email = request.data['email']
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({
            'status':False,
            'message':"no user found with the given email"
            }, status.HTTP_404_NOT_FOUND)
        reset_user = PasswordReset.objects.filter(user=user).first()
        if reset_user:
            return Response({
            'status':False,
            'message':"link already sent to email"
            }, status.HTTP_404_NOT_FOUND)
        
        token = generate_token()
        PasswordReset.objects.create(user=user,token=token)
        # send_password_reset_email(user.email, token)
        reset_url = reverse('user_forgot_pass_confirm', kwargs={'token': token})
        reset_link = request.build_absolute_uri(reset_url)
        return Response({
            'status':True,
            "reset_link":reset_link
        })

class ForgotPassConfirmUser(APIView):
    def post(self, request, token):
        reset_token = PasswordReset.objects.filter(token=token).first()
        if not reset_token:
            return Response({
            'status':False,
            "message":"reset_link invalid"
            })
        user = User.objects.filter(id=reset_token.user.id).first()
        data = request.data
        serializer = ResetPassSerializer(data=data)
        if not serializer.is_valid():
            return Response({
            'status':False,
            "message":serializer.errors
            })
        
        user.set_password(serializer.data["password"])
        user.save()
        reset_token.delete()
        return Response({
            'status':True,
            "message":"password reseted "
        })




class Test(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(request, data):
        utc_time = timezone.now()

        return Response({"message":"test success"})


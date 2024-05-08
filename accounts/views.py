from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NormalUser, User
from django.utils import timezone
from datetime import timedelta
from random import randint
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class RegisterNormalUser(APIView):
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

class VerifyOTPNormalUser(APIView):
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
                user = User.objects.get(email=data['email'])
                if not user:
                        return Response({
                        'status':False,
                        'message':'no user found'
                        }, status.HTTP_404_NOT_FOUND)
                
                normal_user = NormalUser.objects.get(user=user)
                if normal_user.is_verified:
                        return Response({
                        'status':False,
                        'message':'email already verified'
                        }, status.HTTP_406_NOT_ACCEPTABLE)
                
                #time of join of the user
                created = normal_user.otp_gen_time
                #current time
                now = timezone.now() 
                #time difference
                time_difference = now - created
                #time difference should not be greater than 5 min
                if time_difference < timedelta(minutes=5):
                    if data['otp'] == normal_user.otp:
                        normal_user.is_verified = True
                        normal_user.save()
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

class GenarateOTPNormalUser(APIView):
    def post(self, request):
        try:
            data = request.data 
            serializer = GenarateOTPSerializer(data=data)
            if not serializer.is_valid():
                    return Response({
                        'status':False,
                        'message':serializer.errors
                        }, status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.get(email=data['email'])
            normal_user = NormalUser.objects.get(user=user)

            if normal_user.is_verified:
                return Response({
                'status':False,
                'message':'email already verified'
                }, status.HTTP_406_NOT_ACCEPTABLE)
                
            #time of join of the user
            created = normal_user.otp_gen_time
            #current time
            now = timezone.now() 
            #time difference
            time_difference = now - created
            #time difference should not be greater than 5 min

            if time_difference > timedelta(minutes=5):
                #change otp and time
                otp = randint(1000,9999) 
                normal_user.otp = otp
                normal_user.otp_gen_time = timezone.now()
                normal_user.save()
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

class LoginNormalUser(APIView):
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
        
        usr_obj = User.objects.get(username=data['username'])

        normal_user = NormalUser.objects.get(user=usr_obj)

        if not normal_user.is_verified:
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


class Test(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(request, data):
        utc_time = timezone.now()

        return Response({"message":"test success"})


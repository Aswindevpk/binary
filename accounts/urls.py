from django.urls import path
from .views import *

urlpatterns = [
    path('register/',RegisterNormalUser.as_view(),name='user_register'),
    path('test/',Test.as_view(),name='test'),
    path('verify_otp/',VerifyOTPNormalUser.as_view(),name='user_verify_otp'),
    path('genarate_otp/',GenarateOTPNormalUser.as_view(),name='user_genarate_otp'),
    path('login/',LoginNormalUser.as_view(),name='user_login'),
]
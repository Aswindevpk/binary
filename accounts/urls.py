from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',RegisterUser.as_view(),name='user_register'),
    path('verify_otp/',VerifyOTPUser.as_view(),name='user_verify_otp'),
    path('genarate_otp/',GenarateOTPUser.as_view(),name='user_genarate_otp'),
    path('login/',LoginUser.as_view(),name='user_login'),
    path('login/refresh/',TokenRefreshView.as_view(),name='user_token_refresh'),
    path('logout/',LogoutUser.as_view(),name='user_logout'),
    path('forgot_password/',ForgotPassUser.as_view(),name='user_forgot_pass'),
    path('forgot_password_confirm/',ForgotPassConfirmUser.as_view(),name='user_forgot_pass_confirm'),
    path('reset_password/',ResetPassUser.as_view(),name='user_reset_password'),
    path('create_order/', CreateOrderAPIView.as_view(), name='create_order'),
    path('verify_payment/', VerifyPaymentAPIView.as_view(), name='verify_payment'),
]
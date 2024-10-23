from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    #authentication
    path('register/',RegisterView.as_view(),name='user_register'),
    path('login/',LoginView.as_view(),name='user_login'),
    path('login/refresh/',TokenRefreshView.as_view(),name='user_token_refresh'),
    path('logout/',LogoutView.as_view(),name='user_logout'),
    path('resend-otp/',ResendOtpView.as_view(),name='user_resend_otp'),
    path('verify-otp/',VerifyOtpView.as_view(),name='user_verify_otp'),
    path('password-reset/',PasswordResetRequestView.as_view(),name='user_forgot_pass'),
    path('password-reset-confirm/',PasswordResetConfirmView.as_view(),name='user_forgot_pass_confirm'),
    
    #profile updation
    path('profile/',ProfileView.as_view(),name='user_profile'),

    #user actions
    path('<str:uid>/follow/',FollowUserView.as_view(),name='follow_user'),
    path('<str:uid>/unfollow/',UnfollowUserView.as_view(),name='unfollow_user'),
    path('<str:uid>/follow-stats/',UserFollowStatsView.as_view(),name='user_follow-stats'),

    #payment
    path('create_order/', CreateOrderAPIView.as_view(), name='create_order'),
    path('verify_payment/', VerifyPaymentAPIView.as_view(), name='verify_payment'),
]
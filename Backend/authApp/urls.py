from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from authApp.views import (
    SignupAPIView,
    VerifyOTPAPIView,
    ResendOTPAPIView,
    RoleCreateAPIView,
    SocialLoginAPIView,
    RoleLoginAPIView,
    UsernameCheckAPIView,
    RequestPasswordResetAPIView,
    ResetPasswordAPIView,
)


urlpatterns = [
    path('kn/signup/', SignupAPIView.as_view(), name='signup'),
    path('kn/verifyotp/', VerifyOTPAPIView.as_view(), name='signup_ta'),
    path('kn/resend-otp/', ResendOTPAPIView.as_view(), name='resend_otp'),
    path('kn/login/', RoleLoginAPIView.as_view(), name='signup_default'),
    #role api
    path('kn/role/', RoleCreateAPIView.as_view(), name='role_create'),
    
    #Social Auth URLs
    path('kn/social/token/', SocialLoginAPIView.as_view(), name='social_login_token'),
    path('kn/check-username/', UsernameCheckAPIView.as_view(), name='check_username'),

    # Password Reset URLs
    path('kn/password-reset-request/', RequestPasswordResetAPIView.as_view(), name='password_reset_request'),
    path('kn/password-reset-confirm/', ResetPasswordAPIView.as_view(), name='password_reset_confirm'),

    # JWT Token Management
    path('kn/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('kn/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]


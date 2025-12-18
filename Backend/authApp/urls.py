from django.urls import path
from authApp.views import (
    SignupAPIView,
    VerifyOTPAPIView,
    ResendOTPAPIView,
    RoleCreateAPIView,
    SocialLoginAPIView,
    RoleLoginAPIView,
)


urlpatterns = [
    path('kn/signup/', SignupAPIView.as_view(), name='signup'),
    path('kn/verifyotp/', VerifyOTPAPIView.as_view(), name='signup_ta'),
    path('kn/login/', RoleLoginAPIView.as_view(), name='signup_default'),
    #role api
    path('kn/role/', RoleCreateAPIView.as_view(), name='role_create'),
    
    #Social Auth URLs
    path('kn/social/token/', SocialLoginAPIView.as_view(), name='social_login_token'),
    
]


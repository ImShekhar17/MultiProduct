from django.urls import path
from api.views import (
    SignupAPIView,
    VerifyOTPAPIView,
    ResendOTPAPIView,
    LoginAPIView,
    RoleCreateAPIView,
    SocialLoginAPIView,
)


urlpatterns = [
    path('kn/auth/signup/', SignupAPIView.as_view(), name='signup'),
    path('kn/auth/verifyotp/', VerifyOTPAPIView.as_view(), name='signup_ta'),
    path('kn/auth/login/', LoginAPIView.as_view(), name='signup_default'),
    #role api
    path('kn/role/', RoleCreateAPIView.as_view(), name='role_create'),
    
    #Social Auth URLs
    path('auth/social/token/', SocialLoginAPIView.as_view(), name='social_login_token'),
    
]


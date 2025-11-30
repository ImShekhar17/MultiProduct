"""Authentication views for user signup, login, password reset, and role management."""

# Standard Library
import random
from datetime import timedelta

# Third-Party
import requests
import logging

# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone

# Django REST Framework
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# JWT
from rest_framework_simplejwt.tokens import RefreshToken

# Celery Tasks
from authApp.tasks.send_mail_otp import send_email_otp,send_welcome_email

# Project Apps
from authApp.models import User, Role
from authApp.serializers import (
    SignupSerializer,
    RoleSerializer,
    ResetPasswordSerializer,
)

User = get_user_model()

logger = logging.getLogger(__name__)



class SocialLoginAPIView(APIView):
    """
    Social login via Google or Facebook.
    
    POST /auth/social/login/
    {
        "provider": "google" | "facebook",
        "access_token": "<token_from_client>"
    }
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle social login request."""
        provider = request.data.get("provider")
        token = request.data.get("access_token")

        if not provider or not token:
            return Response(
                {"error": "provider and access_token required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if provider == "google":
            user_info = self.verify_google_token(token)
        elif provider == "facebook":
            user_info = self.verify_facebook_token(token)
        else:
            return Response(
                {"error": "Invalid provider"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "error" in user_info:
            return Response(user_info, status=status.HTTP_400_BAD_REQUEST)

        email = user_info.get("email")
        name = user_info.get("name", "No Name")

        if not email:
            return Response(
                {"error": "Email not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create or get user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email, "first_name": name},
        )

        tokens = self.create_jwt(user)

        return Response(
            {
                "message": "Login Successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.first_name,
                },
                "tokens": tokens,
            }
        )

    @staticmethod
    def create_jwt(user):
        """Create JWT tokens for user."""
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    @staticmethod
    def verify_google_token(token):
        """Verify Google OAuth token."""
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        response = requests.get(url).json()

        if "error_description" in response:
            return {"error": "Invalid Google token"}

        return {
            "email": response.get("email"),
            "name": response.get("name"),
        }

    @staticmethod
    def verify_facebook_token(token):
        """Verify Facebook OAuth token."""
        app_id = settings.FACEBOOK_APP_ID
        app_secret = settings.FACEBOOK_APP_SECRET
        debug_url = (
            f"https://graph.facebook.com/debug_token?"
            f"input_token={token}&access_token={app_id}|{app_secret}"
        )

        debug_info = requests.get(debug_url).json()

        if "error" in debug_info.get("data", {}):
            return {"error": "Invalid Facebook token"}

        user_url = (
            f"https://graph.facebook.com/me?fields=id,name,email&access_token={token}"
        )
        user_info = requests.get(user_url).json()

        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
        }


class SignupAPIView(APIView):
    """API for user signup."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle signup request."""
        session = request.session
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)

            if user.is_active:
                return Response(
                    {"error": "User already registered with this email."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # User exists but is inactive → resend OTP
            otp_code = str(random.randint(100000, 999999))
            now = timezone.now()
            session.update(
                {
                    "email": user.email,
                    "otp": otp_code,
                    "otp_expires_at": (now + timedelta(minutes=5)).isoformat(),
                    "otp_requests": [now.isoformat()],
                }
            )
            session.modified = True

            send_email_otp.delay(user.email, otp_code)
            
            # try:
            #     send_email_otp.delay(user.email, otp_code)
            #     logger.info(f"OTP task queued for {user.email}")
            # except Exception as e:
            #     logger.error(f"Failed to queue OTP task: {str(e)}")
            #     # Fallback to synchronous email send
            #     send_email_otp(user.email, otp_code)

            return Response(
                {
                    "message": (
                        "User already exists but not verified. "
                        "OTP has been resent."
                    )
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            # Brand new signup
            serializer = SignupSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()
            user.is_active = False
            user.save(update_fields=["is_active"])

            otp_code = str(random.randint(100000, 999999))
            now = timezone.now()
            session.update(
                {
                    "email": user.email,
                    "otp": otp_code,
                    "otp_expires_at": (now + timedelta(minutes=5)).isoformat(),
                    "otp_requests": [now.isoformat()],
                }
            )
            session.modified = True

            send_email_otp.delay(user.email, otp_code)

            # try:
            #     send_email_otp.delay(user.email, otp_code)
            #     logger.info(f"OTP task queued for {user.email}")
            # except Exception as e:
            #     logger.error(f"Failed to queue OTP task: {str(e)}")
            #     # Fallback to synchronous email send
            #     send_email_otp(user.email, otp_code)

            
            
            return Response(
                {"message": "Signup successful. OTP sent to your email."},
                status=status.HTTP_201_CREATED,
            )


class VerifyOTPAPIView(APIView):
    """API to verify OTP during signup."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Verify OTP provided by user."""
        session = request.session
        otp_input = request.data.get("otp")
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp_input:
            return Response(
                {"error": "Otp is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stored_otp = session.get("otp")
        otp_expiry_str = session.get("otp_expires_at")

        if not stored_otp or stored_otp != otp_input:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp_expiry_str:
            return Response(
                {
                    "error": (
                        "OTP expiration time not found. "
                        "Please request a new OTP."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert string back to datetime
        otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)

        if timezone.now() > otp_expiry:
            return Response(
                {"error": "OTP has expired. Request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Activate user
        user.is_active = True
        user.save(update_fields=["is_active"])

        # Clear session data
        for key in ["otp", "otp_expires_at", "email"]:
            session.pop(key, None)
        session.modified = True
        
        send_welcome_email.delay(user.email, user.first_name)

        return Response(
            {
                "message": "OTP verified. Signup complete.",
                "username": user.username,
            },
            status=status.HTTP_200_OK,
        )


class ResendOTPAPIView(APIView):
    """API to resend OTP to user email."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Resend OTP with rate limiting."""
        session = request.session
        email = session.get("email") or request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_requests = session.get("otp_requests", [])
        now = timezone.now()

        # Filter only recent (valid) OTP requests
        valid_otp_requests = [
            t
            for t in otp_requests
            if now - timezone.datetime.fromisoformat(t) < timedelta(minutes=10)
        ]

        if len(valid_otp_requests) >= 3:
            return Response(
                {"error": "Too many OTP requests. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))

        # Update session
        session["email"] = email
        session["otp"] = otp_code
        session["otp_expires_at"] = (now + timedelta(minutes=5)).isoformat()
        valid_otp_requests.append(now.isoformat())
        session["otp_requests"] = valid_otp_requests
        session.modified = True

        send_email_otp.delay(email, otp_code)

        return Response(
            {"message": "New OTP sent to your email."},
            status=status.HTTP_200_OK,
        )


class LoginAPIView(APIView):
    """API to authenticate users using multiple login methods."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle login with email/mobile + password or email + OTP."""
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        otp = request.data.get("otp")

        session = request.session

        # Case 1: Login with Email & Password
        if email and password:
            return self._login_with_email_password(email, password)

        # Case 2: Login with Mobile Number & Password
        if phone_number and password:
            return self._login_with_mobile_password(phone_number, password)

        # Case 3: Login with Email & OTP
        if email and otp:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "User with this email does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return self._verify_otp_login(session, user, otp)

        return Response(
            {"error": "Invalid login credentials."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @staticmethod
    def _login_with_email_password(email, password):
        """Login with email and password."""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {
                    "error": (
                        "User account is inactive. Verify OTP first."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return LoginAPIView._generate_login_response(user)

    @staticmethod
    def _login_with_mobile_password(phone_number, password):
        """Login with mobile number and password."""
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this mobile number does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {
                    "error": (
                        "User account is inactive. Verify OTP first."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return LoginAPIView._generate_login_response(user)

    @staticmethod
    def _generate_login_response(user):
        """Generate response upon successful login."""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response(
            {
                "message": "Login successful.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "username": user.username,
                },
                "token": access_token,
                "refresh_token": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _verify_otp_login(session, user, otp_input):
        """Verify OTP for login."""
        stored_otp = session.get("otp")
        otp_expiry_str = session.get("otp_expires_at")

        if not stored_otp or stored_otp != otp_input:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp_expiry_str:
            return Response(
                {
                    "error": (
                        "OTP expiration time not found. "
                        "Request a new OTP."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)

        if timezone.now() > otp_expiry:
            return Response(
                {"error": "OTP has expired. Request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Clear OTP session after successful verification
        for key in ["otp", "otp_expires_at", "email"]:
            session.pop(key, None)
        session.modified = True

        return LoginAPIView._generate_login_response(user)


class RoleLoginAPIView(APIView):
    """API to authenticate users with role included in token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle login with role in JWT token."""
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        otp = request.data.get("otp")

        session = request.session

        # Case 1: Login with Email & Password
        if email and password:
            return self._login_with_email_password(email, password)

        # Case 2: Login with Mobile Number & Password
        if phone_number and password:
            return self._login_with_mobile_password(phone_number, password)

        # Case 3: Login with Email & OTP
        if email and otp:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "User with this email does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return self._verify_otp_login(session, user, otp)

        return Response(
            {"error": "Invalid login credentials."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @staticmethod
    def _login_with_email_password(email, password):
        """Login with email and password."""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {
                    "error": (
                        "User account is inactive. Verify OTP first."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return RoleLoginAPIView._generate_login_response(user)

    @staticmethod
    def _login_with_mobile_password(phone_number, password):
        """Login with mobile number and password."""
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this mobile number does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {
                    "error": (
                        "User account is inactive. Verify OTP first."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return RoleLoginAPIView._generate_login_response(user)

    @staticmethod
    def _generate_login_response(user):
        """Generate response upon successful login with role."""
        refresh = RefreshToken.for_user(user)

        # Add custom claims to the token
        refresh["user_id"] = str(user.id)
        refresh["username"] = user.username
        refresh["email"] = user.email
        refresh["role"] = user.role.name if user.role else None

        return Response(
            {
                "message": "Login successful.",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "role": user.role.name if user.role else None,
                    "phone_number": user.phone_number,
                    "username": user.username,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _verify_otp_login(session, user, otp_input):
        """Verify OTP for login."""
        stored_otp = session.get("otp")
        otp_expiry_str = session.get("otp_expires_at")

        if not stored_otp or stored_otp != otp_input:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp_expiry_str:
            return Response(
                {
                    "error": (
                        "OTP expiration time not found. "
                        "Request a new OTP."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)

        if timezone.now() > otp_expiry:
            return Response(
                {"error": "OTP has expired. Request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Clear OTP session after successful verification
        for key in ["otp", "otp_expires_at", "email"]:
            session.pop(key, None)
        session.modified = True

        return RoleLoginAPIView._generate_login_response(user)


class RequestPasswordResetAPIView(APIView):
    """API to request password reset."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Send password reset link to email."""
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate a password reset token and encode user ID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = (
            f"{settings.FRONTEND_URL}/reset-password/?uid={uid}&token={token}"
        )

        # Send email with reset link (async preferred)
        from authApp.tasks.send_mail_otp import send_password_reset_email
        send_password_reset_email.delay(email, reset_url)

        return Response(
            {"message": "Password reset link sent to your email."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordAPIView(APIView):
    """API to reset password using token from query params."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Reset password with valid reset token."""
        uidb64 = request.query_params.get("uid")
        token = request.query_params.get("token")

        if not uidb64 or not token:
            return Response(
                {"error": "Missing reset token or user ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Decode user ID from base64
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"error": "Invalid user ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the token
        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate new password
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update user's password
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class RoleCreateAPIView(APIView):
    """API for CRUD operations on roles."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Retrieve all roles."""
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new role."""
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            return Response(
                RoleSerializer(role).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        """Partially update a role."""
        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response(
                {"error": "Role not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RoleSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            role = serializer.save()
            return Response(
                RoleSerializer(role).data,
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        """Delete a role."""
        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response(
                {"error": "Role not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        role.delete()
        return Response(
            {"message": "Role deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

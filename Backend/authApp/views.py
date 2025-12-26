"""Authentication views for user signup, login, password reset, and role management."""

# Standard Library
import random
from datetime import timedelta

# Third-Party
import requests
import logging

# Django
from django.conf import settings
from django.db import transaction
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
from authApp.models import User, Role, UserOTP
from authApp.serializers import (
    SignupSerializer,
    RoleSerializer,
    ResetPasswordSerializer,
    LoginSerializer,
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
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Enterprise Rate Limiting: Max 10 signups/OTPs per day per account to prevent email abuse
        one_day_ago = timezone.now() - timedelta(days=1)
        daily_count = UserOTP.objects.filter(user__email=email, created_at__gt=one_day_ago).count()
        if daily_count >= 10:
            return Response(
                {"error": "Too many verification requests. Please try again tomorrow."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            # Atomic operation for data consistency
            with transaction.atomic():
                user = User.objects.select_for_update().get(email=email)

                if user.is_active:
                    return Response(
                        {"error": "User already registered and verified with this email."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Resend OTP for existing inactive user
                return self._process_otp_flow(user, "User already exists but not verified. A new OTP has been sent.")

        except User.DoesNotExist:
            serializer = SignupSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                user = serializer.save()
                user.is_active = False # Explicitly inactive
                user.save(update_fields=["is_active"])
                
                return self._process_otp_flow(user, "Signup successful. OTP sent to your email.", status.HTTP_201_CREATED)

    def _process_otp_flow(self, user, success_message, status_code=status.HTTP_200_OK):
        """Helper for OTP generation with high-performance cleanup and dispatch."""
        otp_code = str(random.randint(100000, 999999))
        
        # Self-Cleaning: Invalidate all existing unused OTPs for this user to keep index small
        with transaction.atomic():
            UserOTP.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Save new OTP to DB
            UserOTP.objects.create(
                user=user,
                otp_code=otp_code,
                expires_at=timezone.now() + timedelta(minutes=10)
            )

        # Dispatch async email
        send_email_otp.delay(user.email, otp_code)
        
        return Response({"message": success_message}, status=status_code)



class VerifyOTPAPIView(APIView):
    """
    API to verify OTP during signup.
    Uses persistent DB verification.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        otp_input = request.data.get("otp")
        email = request.data.get("email")

        if not (email and otp_input):
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        # High-concurrency protection using select_for_update
        with transaction.atomic():
            # Lookup non-expired, unused OTP in DB and lock the row
            otp_record = UserOTP.objects.filter(
                user=user,
                is_used=False,
                expires_at__gt=timezone.now()
            ).select_for_update().first()

            if not otp_record:
                return Response({"error": "No active OTP found for this account."}, status=status.HTTP_400_BAD_REQUEST)

            # Brute-force protection: check if account is already locked
            if otp_record.failed_attempts >= 5:
                # Mark as used to prevent further attempts on this specific OTP
                otp_record.is_used = True
                otp_record.save(update_fields=["is_used"])
                return Response({"error": "Too many failed attempts. This OTP is now void. Please request a new one."}, status=status.HTTP_403_FORBIDDEN)

            # Case: Incorrect OTP
            if otp_record.otp_code != otp_input:
                otp_record.failed_attempts += 1
                otp_record.save(update_fields=["failed_attempts"])
                
                remaining = 5 - otp_record.failed_attempts
                error_msg = f"Invalid OTP. {remaining} attempts remaining." if remaining > 0 else "Too many failed attempts. OTP invalidated."
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

            # Case: Correct OTP - Activate user and mark OTP as used
            user.is_active = True
            user.save(update_fields=["is_active"])
            
            otp_record.is_used = True
            otp_record.save(update_fields=["is_used"])
        
        # Async welcome email
        send_welcome_email.delay(user.email, user.first_name)

        return Response(
            {
                "message": "OTP verified successfully. Signup complete.",
                "username": user.username,
            },
            status=status.HTTP_200_OK,
        )


class ResendOTPAPIView(APIView):
    """
    API to resend OTP with persistent rate limiting.
    Optimized for heavy traffic with indexed DB lookups.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Account not found."}, status=status.HTTP_400_BAD_REQUEST)

        # High-Load Rate Limiting (Max 3 requests in 10 minutes)
        ten_mins_ago = timezone.now() - timedelta(minutes=10)
        recent_requests = UserOTP.objects.filter(
            user=user, 
            created_at__gt=ten_mins_ago
        ).count()

        if recent_requests >= 3:
            return Response(
                {"error": "Too many attempts. Please wait 10 minutes."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Enterprise Daily Limit Check
        one_day_ago = timezone.now() - timedelta(days=1)
        daily_count = UserOTP.objects.filter(user=user, created_at__gt=one_day_ago).count()
        if daily_count >= 10:
            return Response(
                {"error": "Daily verification limit reached. Try again tomorrow."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Generate and save new OTP using the signup helper logic for consistency
        # Assuming we want to share the logic, we'd ideally have it in a mixin, 
        # but for now we'll duplicate the fix for Signup/Resend for clarity.
        otp_code = str(random.randint(100000, 999999))
        with transaction.atomic():
            UserOTP.objects.filter(user=user, is_used=False).update(is_used=True)
            UserOTP.objects.create(
                user=user,
                otp_code=otp_code,
                expires_at=timezone.now() + timedelta(minutes=10)
            )

        send_email_otp.delay(email, otp_code)
        return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)


# class LoginAPIView(APIView):
#     """API to authenticate users using multiple login methods."""

#     permission_classes = [AllowAny]

#     def post(self, request):
#         """Handle login with email/mobile + password or email + OTP."""
#         email = request.data.get("email")
#         phone_number = request.data.get("phone_number")
#         password = request.data.get("password")
#         otp = request.data.get("otp")

#         session = request.session

#         # Case 1: Login with Email & Password
#         if email and password:
#             return self._login_with_email_password(email, password)

#         # Case 2: Login with Mobile Number & Password
#         if phone_number and password:
#             return self._login_with_mobile_password(phone_number, password)

#         # Case 3: Login with Email & OTP
#         if email and otp:
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 return Response(
#                     {"error": "User with this email does not exist."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             return self._verify_otp_login(session, user, otp)

#         return Response(
#             {"error": "Invalid login credentials."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     @staticmethod
#     def _login_with_email_password(email, password):
#         """Login with email and password."""
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response(
#                 {"error": "User with this email does not exist."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if not user.is_active:
#             return Response(
#                 {
#                     "error": (
#                         "User account is inactive. Verify OTP first."
#                     )
#                 },
#                 status=status.HTTP_403_FORBIDDEN,
#             )

#         if not user.check_password(password):
#             return Response(
#                 {"error": "Invalid password."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         return LoginAPIView._generate_login_response(user)

#     @staticmethod
#     def _login_with_mobile_password(phone_number, password):
#         """Login with mobile number and password."""
#         try:
#             user = User.objects.get(phone_number=phone_number)
#         except User.DoesNotExist:
#             return Response(
#                 {"error": "User with this mobile number does not exist."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if not user.is_active:
#             return Response(
#                 {
#                     "error": (
#                         "User account is inactive. Verify OTP first."
#                     )
#                 },
#                 status=status.HTTP_403_FORBIDDEN,
#             )

#         if not user.check_password(password):
#             return Response(
#                 {"error": "Invalid password."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         return LoginAPIView._generate_login_response(user)

#     @staticmethod
#     def _generate_login_response(user):
#         """Generate response upon successful login."""
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)
#         return Response(
#             {
#                 "message": "Login successful.",
#                 "user": {
#                     "id": user.id,
#                     "email": user.email,
#                     "phone_number": user.phone_number,
#                     "username": user.username,
#                 },
#                 "access_token": access_token,
#                 "refresh_token": str(refresh),
#             },
#             status=status.HTTP_200_OK,
#         )

#     @staticmethod
#     def _verify_otp_login(session, user, otp_input):
#         """Verify OTP for login."""
#         stored_otp = session.get("otp")
#         otp_expiry_str = session.get("otp_expires_at")

#         if not stored_otp or stored_otp != otp_input:
#             return Response(
#                 {"error": "Invalid OTP."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if not otp_expiry_str:
#             return Response(
#                 {
#                     "error": (
#                         "OTP expiration time not found. "
#                         "Request a new OTP."
#                     )
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)

#         if timezone.now() > otp_expiry:
#             return Response(
#                 {"error": "OTP has expired. Request a new OTP."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Clear OTP session after successful verification
#         for key in ["otp", "otp_expires_at", "email"]:
#             session.pop(key, None)
#         session.modified = True

#         return LoginAPIView._generate_login_response(user)


class RoleLoginAPIView(APIView):
    """
    Optimized API for role-based authentication.
    Handles Email/Password, Phone/Password, and Email/OTP methods.
    Engineered for high load (50k+ requests) with efficient DB transactions.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        valid_data = serializer.validated_data
        email = valid_data.get("email")
        phone_number = valid_data.get("phone_number")
        password = valid_data.get("password")
        otp = valid_data.get("otp")

        # Prioritize authentication method
        if password:
            if email:
                return self._login_with_password(email=email, password=password)
            if phone_number:
                return self._login_with_password(phone_number=phone_number, password=password)
        
        if email and otp:
            return self._login_with_otp(email, otp)

        return Response(
            {"error": "Invalid combination of login credentials."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _login_with_password(self, email=None, phone_number=None, password=None):
        """Authenticates using password with optimized DB lookup."""
        try:
            query = {"email": email} if email else {"phone_number": phone_number}
            # Use select_related if user holds a direct foreign key to role for performance
            user = User.objects.select_related('role').get(**query)
        except User.DoesNotExist:
            return Response(
                {"error": "Account not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"error": "Account is inactive. Please verify OTP first."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self._generate_response(user)

    def _login_with_otp(self, email, otp_code):
        """Verifies persistent OTP from database for high-load reliability."""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # High-concurrency protection using select_for_update
        with transaction.atomic():
            # Check for non-expired, unused OTP and lock the row
            otp_record = UserOTP.objects.filter(
                user=user, 
                is_used=False,
                expires_at__gt=timezone.now()
            ).select_for_update().first()

            if not otp_record:
                return Response(
                    {"error": "Invalid or expired OTP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Brute-force protection
            if otp_record.failed_attempts >= 5:
                # Mark as used to prevent further attempts on this specific OTP
                otp_record.is_used = True
                otp_record.save(update_fields=["is_used"])
                return Response({"error": "Too many failed attempts. This OTP is now void. Please request a new one."}, status=status.HTTP_403_FORBIDDEN)

            # Case: Incorrect OTP
            if otp_record.otp_code != otp_code:
                otp_record.failed_attempts += 1
                otp_record.save(update_fields=["failed_attempts"])
                
                remaining = 5 - otp_record.failed_attempts
                error_msg = f"Invalid OTP. {remaining} attempts remaining." if remaining > 0 else "Too many failed attempts. OTP invalidated."
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

            # Mark OTP as used atomically
            otp_record.is_used = True
            otp_record.save(update_fields=["is_used"])

        return self._generate_response(user)

    @staticmethod
    def _generate_response(user):
        """Generates a professional JWT response with role information."""
        refresh = RefreshToken.for_user(user)
        
        # Add role to access token payload for high-load optimization
        role_name = user.role.name if user.role else None
        refresh['role'] = role_name
        
        return Response(
            {
                "message": "Login successful.",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "username": user.username,
                    "role": role_name
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


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

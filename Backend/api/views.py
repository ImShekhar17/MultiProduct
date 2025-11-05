from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rst_framework.pagination import PageNumberPagination,LimitOffPagination
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import random
from datetime import timedelta

#------
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import TranslatedText
from .services import process_text_with_translation
from .serializers import TranslatedTextSerializer

#-----
from .models import *
from .serializers import *

# Create your views here.



class SignupAPIView(APIView):
    def post(self, request):
        session = request.session
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            if user.is_active:
                return Response({"error": "User already registered with this email."}, status=status.HTTP_400_BAD_REQUEST)

            # User exists but is inactive → resend OTP
            otp_code = str(random.randint(100000, 999999))
            now = timezone.now()
            session.update({
                "email": user.email,
                "otp": otp_code,
                "otp_expires_at": (now + timedelta(minutes=5)).isoformat(),
                "otp_requests": [now.isoformat()]
            })
            session.modified = True

            send_email_otp(user.email, otp_code)

            return Response({"message": "User already exists but not verified. OTP has been resent."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Brand new signup
            serializer = SignupSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            user.is_active = False
            user.save(update_fields=["is_active"])

            otp_code = str(random.randint(100000, 999999))
            now = timezone.now()
            session.update({
                "email": user.email,
                "otp": otp_code,
                "otp_expires_at": (now + timedelta(minutes=5)).isoformat(),
                "otp_requests": [now.isoformat()]
            })
            session.modified = True

            send_email_otp(user.email, otp_code)

            return Response({"message": "Signup successful. OTP sent to your email."}, status=status.HTTP_201_CREATED)


class VerifyOTPAPIView(APIView):
    def post(self, request):
        session = request.session
        otp_input = request.data.get("otp")
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_input:
            return Response({"error": "Otp is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        stored_otp = session.get("otp")
        otp_expiry_str = session.get("otp_expires_at")

        if not stored_otp or stored_otp != otp_input:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_expiry_str:
            return Response({"error": "OTP expiration time not found. Please request a new OTP."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Convert string back to datetime
        otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)

        if timezone.now() > otp_expiry:
            return Response({"error": "OTP has expired. Request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Activate user and generate application ID
        user.is_active = True
        if not user.application_id:
            user.application_id = user.generate_application_id()
        user.save(update_fields=["is_active", "application_id"])

        # Clear session data
        for key in ["otp", "otp_expires_at", "email"]:
            session.pop(key, None)
        session.modified = True

        # Send email to the user
        subject = "Your Application ID"
        message = f"Dear {user.name},\n\nYour application ID is: {user.application_id}.\n\nThank you for registering!"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        return Response({
            "message": "OTP verified. Signup complete. Application ID has been sent to your email.",
            "application_id": user.application_id
        }, status=status.HTTP_200_OK)

class ResendOTPAPIView(APIView):
    def post(self, request):
        session = request.session
        email = session.get("email") or request.data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        otp_requests = session.get("otp_requests", [])
        now = timezone.now()

        # Filter only recent (valid) OTP requests
        valid_otp_requests = [
            t for t in otp_requests
            if now - timezone.datetime.fromisoformat(t) < timedelta(minutes=10)
        ]

        if len(valid_otp_requests) >= 3:
            return Response({"error": "Too many OTP requests. Try again later."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))

        # Update session
        session["email"] = email
        session["otp"] = otp_code
        session["otp_expires_at"] = (now + timedelta(minutes=5)).isoformat()
        valid_otp_requests.append(now.isoformat())
        session["otp_requests"] = valid_otp_requests
        session.modified = True

        send_email_otp(email, otp_code)

        return Response({"message": "New OTP sent to your email."}, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    """ API to authenticate users using multiple login methods """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        mobile_number = request.data.get("mobile_number")
        application_id = request.data.get("application_id")
        password = request.data.get("password")
        otp = request.data.get("otp")

        session = request.session

        # Case 1: Login with Email & Password
        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({"error": "User account is inactive. Verify OTP first."}, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(password):
                return Response({"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

            return self.generate_login_response(user)

        # Case 2: Login with Mobile Number & Password
        elif mobile_number and password:
            try:
                user = User.objects.get(mobile_number=mobile_number)
            except User.DoesNotExist:
                return Response({"error": "User with this mobile number does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({"error": "User account is inactive. Verify OTP first."}, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(password):
                return Response({"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

            return self.generate_login_response(user)

        # Case 3: Login with Application ID & Password
        elif application_id and password:
            try:
                user = User.objects.get(application_id=application_id)
            except User.DoesNotExist:
                return Response({"error": "User with this application ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({"error": "User account is inactive. Verify OTP first."}, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(password):
                return Response({"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

            return self.generate_login_response(user)

        # Case 4: Login with Email & OTP
        elif email and otp:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            return self.verify_otp_login(session, user, otp)

        # Case 5: Login with Application ID & OTP
        elif application_id and otp:
            try:
                user = User.objects.get(application_id=application_id)
            except User.DoesNotExist:
                return Response({"error": "User with this application ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            return self.verify_otp_login(session, user, otp)

        else:
            return Response({"error": "Invalid login credentials."}, status=status.HTTP_400_BAD_REQUEST)

    def generate_login_response(self, user):
        """ Generate response upon successful login """
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response({
            "message": "Login successful.",
            "user": {

                "id": user.id,
                "email": user.email,
                "mobile_number": user.mobile_number,
                "application_id": user.application_id,
                "name": user.name
            },
            "token": access_token,
            "refresh_token": str(refresh)
        }, status=status.HTTP_200_OK)

    def verify_otp_login(self, session, user, otp_input):
        """ Verify OTP for login """
        stored_otp = session.get("otp")
        otp_expiry_str = session.get("otp_expires_at")

        if not stored_otp or stored_otp != otp_input:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_expiry_str:
            return Response({"error": "OTP expiration time not found. Request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

        otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)

        if timezone.now() > otp_expiry:
            return Response({"error": "OTP has expired. Request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP session after successful verification
        for key in ["otp", "otp_expires_at", "email"]:
            session.pop(key, None)
        session.modified = True

        return self.generate_login_response(user)




# for include user role in token

class RoleLoginAPIView(APIView):
    """ API to authenticate users using multiple login methods """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        mobile_number = request.data.get("mobile_number")
        application_id = request.data.get("application_id")
        password = request.data.get("password")
        otp = request.data.get("otp")

        session = request.session

        # Case 1: Login with Email & Password
        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({"error": "User account is inactive. Verify OTP first."}, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(password):
                return Response({"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

            return self.generate_login_response(user)

        # Case 2: Login with Mobile Number & Password
        elif mobile_number and password:
            try:
                user = User.objects.get(mobile_number=mobile_number)
            except User.DoesNotExist:
                return Response({"error": "User with this mobile number does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({"error": "User account is inactive. Verify OTP first."}, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(password):
                return Response({"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

            return self.generate_login_response(user)

        # Case 3: Login with Application ID & Password
        elif application_id and password:
            try:
                user = User.objects.get(application_id=application_id)
            except User.DoesNotExist:
                return Response({"error": "User with this application ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({"error": "User account is inactive. Verify OTP first."}, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(password):
                return Response({"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

            return self.generate_login_response(user)

        # Case 4: Login with Email & OTP
        elif email and otp:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            return self.verify_otp_login(session, user, otp)

        # Case 5: Login with Application ID & OTP
        elif application_id and otp:
            try:
                user = User.objects.get(application_id=application_id)
            except User.DoesNotExist:
                return Response({"error": "User with this application ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            return self.verify_otp_login(session, user, otp)

        else:
            return Response({"error": "Invalid login credentials."}, status=status.HTTP_400_BAD_REQUEST)

    def generate_login_response(self, user):
        """ Generate response upon successful login """
        refresh = RefreshToken.for_user(user)

        # Add custom claims to the token
        refresh['user_id'] = str(user.id)
        refresh['username'] = user.username
        refresh['email'] = user.email
        refresh['role'] = user.role.name if user.role else None

        return Response({
            "message": "Login successful.",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role.name if user.role else None,
                "mobile_number": user.mobile_number,
                "application_id": user.application_id,
                "name": user.name,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)
        
    def verify_otp_login(self, session, user, otp_input):
        """ Verify OTP for login """
        stored_otp = session.get("otp")
        otp_expiry_str = session.get("otp_expires_at")

        if not stored_otp or stored_otp != otp_input:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_expiry_str:
            return Response({"error": "OTP expiration time not found. Request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

        otp_expiry = timezone.datetime.fromisoformat(otp_expiry_str)

        if timezone.now() > otp_expiry:
            return Response({"error": "OTP has expired. Request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP session after successful verification
        for key in ["otp", "otp_expires_at", "email"]:
            session.pop(key, None)
        session.modified = True

        return self.generate_login_response(user)




class RequestPasswordResetAPIView(APIView):
    """ API to request password reset for logged-in user """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a password reset token and encode user ID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/?uid={uid}&token={token}"

        # Send email with reset link
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

        return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    """ API to reset password using token from query params """

    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.query_params.get("uid")
        token = request.query_params.get("token")

        if not uidb64 or not token:
            return Response({"error": "Missing reset token or user ID."}, status=status.HTTP_400_BAD_REQUEST)

        # Decode user ID from base64
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the token
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate new password
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update user's password
        user.password = make_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


class TranslatedTextViewSet(viewsets.ModelViewSet):
    
    """
        POST text to /api/translated-texts/process_text/
        Get translations via /api/translated-texts/{id}/get_translation/?language=hi
    """
    queryset = TranslatedText.objects.all()
    serializer_class = TranslatedTextSerializer

    @action(detail=False, methods=['post'])
    def process_text(self, request):
        text = request.data.get('text')
        if not text:
            return Response({'error': 'Text is required'}, status=400)
            
        try:
            translated_text = process_text_with_translation(text)
            return Response(self.serializer_class(translated_text).data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['get'])
    def get_translation(self, request, pk=None):
        instance = self.get_object()
        language = request.query_params.get('language')
        
        if not language:
            return Response({'error': 'Language code is required'}, status=400)
            
        translation = instance.get_translation(language)
        return Response({
            'original': instance.original_text,
            'original_language': instance.original_language,
            'translated': translation,
            'target_language': language
        })
        
        

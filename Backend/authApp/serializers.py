from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError
from django.conf import settings

from authApp.models import *


User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'


class RolelistSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Role
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # ID as string
        data['id'] = str(instance.id)

        # Group as "uuid_groupname" if exists
        if instance.group:
            data['group'] = f"{instance.group.id}_{instance.group.name}"
        else:
            data['group'] = None
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'user_roles', 'is_active']


class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password", "phone_number",
                  "first_name", "last_name", 'date_of_birth', 'gender', 'address']
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        """Validates user input before creating a user"""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Email already registered."})

        return data

    def create(self, validated_data):
        """Creates a user and securely sets the password"""
        validated_data.pop("confirm_password")
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            gender=validated_data["gender"],
            address=validated_data["address"],
            date_of_birth=validated_data["date_of_birth"],
            is_active=False  # User is inactive until OTP is verified
        )
        user.set_password(validated_data["password"])  # Securely set password
        user.save()
        return user


class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    # def validate_base_price(self, data):
    #     if 'base_price' in data and not data['base_price'] >= 0:
    #         raise ValidationError("Product base price must be a positive number.")
    #     return data/c


# class TranslatedTextSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TranslatedText
#         fields = '__all__'
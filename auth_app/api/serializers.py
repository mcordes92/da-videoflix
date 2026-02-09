"""Serializers for authentication API."""
import uuid, secrets

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import serializers

from auth_app.models import UserTokenModel

class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password confirmation."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate_confirmed_password(self, value):
        """Validate that the confirmed password matches the password."""
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value


    def validate_email(self, value):
        """Validate that the email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value


    def save(self):
        """Create and save a new user with hashed password."""
        pw = self.validated_data['password']

        account = User(email=self.validated_data['email'], username=self.validated_data['email'])
        account.set_password(pw)
        account.is_active = False
        account.save()

        user_data = UserTokenModel(user=account, token=secrets.token_urlsafe(20))
        user_data.save()

        return account
    
class ActivationResponseSerializer(serializers.Serializer):
    """Serializer for account activation response."""
    message = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with email and password."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate user credentials and account activation status."""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials."})
        
        if not user.is_active:
            raise serializers.ValidationError({"detail": "Account is not activated."})
        
        attrs["user"] = user
        return attrs
    

class PasswordResetSerializer(serializers.Serializer):
    """Serializer for requesting a password reset."""
    
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a password reset with new password."""
    
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        """Validate that new password and confirm password match."""
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    
"""Serializers for authentication API."""
import uuid, secrets

from django.contrib.auth.models import User

from rest_framework import serializers

from auth_app.models import UserDataModel

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

        user_data = UserDataModel(user=account, token=secrets.token_urlsafe(20))
        user_data.save()

        return account
    
class ActivationResponseSerializer(serializers.Serializer):
    """Serializer for account activation response."""
    message = serializers.CharField()
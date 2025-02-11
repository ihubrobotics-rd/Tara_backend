from rest_framework import serializers
from accounts.models import *
from django.contrib.auth.hashers import make_password


class CustomUserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=False)
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 
                  'password1', 'password2', 'profile_pic', 'role']
        extra_kwargs = {
            'password1': {'write_only': True},
            'password2': {'write_only': True},
            'role': {'required': False},  
        }

    def validate(self, attrs):
        if attrs.get('password1') != attrs.get('password2'):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2')
        validated_data['password'] = make_password(password)
        return super().create(validated_data)

    def validate_email(self, value):
        """
        Ensure email is unique, excluding the current user.
        """
        user_id = self.instance.id if self.instance else None
        if CustomUser.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        """
        Ensure username is unique, excluding the current user.
        """
        user_id = self.instance.id if self.instance else None
        if CustomUser.objects.filter(username=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value



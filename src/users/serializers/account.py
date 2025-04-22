from rest_framework import serializers

from general.utils.otp import generate_otp
from users.models import UserAccount
from general.utils.otp import generate_user_token, get_user_by_token
import re


class ActivateAccountSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    re_password = serializers.CharField(required=True)

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError('Invalid username')
        return value

    def validate(self, attrs):
        super().validate(attrs)

        if attrs['password'] != attrs['re_password']:
            raise serializers.ValidationError('Passwords do not match.')

        email = get_user_by_token(attrs['token'])
        if not email:
            raise serializers.ValidationError('Token is invalid. Try again.')
        
        user = UserAccount.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError('User does not exist')
        
        if UserAccount.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError('Username already exists.')

        attrs['email'] = email
        
        return attrs


    def create(self, validated_data):
        user = UserAccount.objects.filter(email=validated_data['email']).first()

        user.set_password(validated_data['password'])
        user.username = validated_data['username']
        user.is_active = True
        user.save()
        return user

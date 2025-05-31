from rest_framework import serializers

from general.utils.otp import generate_otp
from users.models import UserAccount


class RequestOTPSerializer(serializers.Serializer):
    receiver = serializers.EmailField(required=True)


class VerifyOtpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)


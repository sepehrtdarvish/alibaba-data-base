from rest_framework import serializers

from general.utils.otp import generate_otp
from users.models import UserAccount


class RequestOTPSerializer(serializers.Serializer):
    receiver = serializers.EmailField(required=True)

    def validate(self, attrs):
        super().validate(attrs)
        if not UserAccount.objects.filter(email=attrs['receiver']).exists():
            # TODO: remove user creation
            user = UserAccount.objects.create_company_owner(email=attrs['receiver'])

            # raise serializers.ValidationError('User does not exist')
        else:
            user = UserAccount.objects.filter(email=attrs['receiver']).first()

        return attrs



class VerifyOtpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)


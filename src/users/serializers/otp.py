from rest_framework import serializers

from general.utils.otp import generate_otp
from users.models import UserAccount
from users.utils import get_user_or_404, detect_identifier_type



class RequestOTPSerializer(serializers.Serializer):
    receiver = serializers.EmailField(required=True)


class RequestLoginOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=100)

    def validate(self, attrs):
        identifier = attrs['identifier']
        type = detect_identifier_type(identifier=identifier)
        user = get_user_or_404(identifier=identifier, type=type)
        
        if type == 'otp':
            if attrs.get('password', None):
                raise serializers.ValidationError('Login with otp does not require password')

        attrs['user'] = user
        
        return attrs
    
    
class VerifyOtpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)

    def validate_email(self, obj):
        if UserAccount.objects.filter(email=obj).exists():
            raise serializers.ValidationError("User already exsits.")
        
        return obj
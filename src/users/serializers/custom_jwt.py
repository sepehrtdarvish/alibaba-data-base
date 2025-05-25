from rest_framework_simplejwt.serializers import *


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {'no_active_account': 'There is no active accoutn with this information.'}

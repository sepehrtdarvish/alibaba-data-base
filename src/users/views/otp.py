from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from general.utils.otp import generate_otp, generate_user_token, verify_otp
from general.utils.gmail_sender import GmailSender
from users.serializers import RequestOTPSerializer, VerifyOtpRequestSerializer


class OTPView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = RequestOTPSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data

        try:
            verification_code = generate_otp(data['receiver'])
            
            gmail_sender = GmailSender()
            
            gmail_sender.send(
                dest_gmail_address=serializer.validated_data['receiver'],
                subject='Ali baba Verifaction Code',
                email_body = f"""
                    Hello,

                    We received a request to verify your account.

                    Your verification code is:
                    {verification_code}

                    Please enter this code within the next 10 minutes.

                    If you did not request this code, please ignore this email.

                    Best regards,  
                    Your Support Team
                    """
                )
                
            return Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



    def post(self, request):
        serializer = VerifyOtpRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if verify_otp(data['receiver'], data['code']):
                token = generate_user_token(data['receiver'])
                return Response(status=status.HTTP_200_OK, data={'token': token})
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

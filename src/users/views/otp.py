from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from general.utils.otp import generate_otp, generate_user_token, verify_otp
from general.utils.gmail_sender import GmailSender

from users.models import UserAccount
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
                dest_gmail_address=data['receiver'],
                subject='Alibaba Verification Code',
                body = f"""
                    Hello,

                    We received a request to verify your account.

                    Your verification code is:
                    {verification_code}

                    Please enter this code within the next 10 minutes.

                    If you did not request this code, please ignore this email.

                    Best regards,  
                    Alibaba Support Team.
                    """
                )
            
            return Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        serializer = VerifyOtpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        code = serializer.validated_data.get('code')

        if verify_otp(email, code):
            UserAccount.objects.create(
                email = email,
                is_superuser = False,
                is_company_owner = False,
                is_staff = False
            )

            token = generate_user_token(email)

            return Response(data={'token': token}, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "Invalid code"}, status=status.HTTP_401_UNAUTHORIZED)

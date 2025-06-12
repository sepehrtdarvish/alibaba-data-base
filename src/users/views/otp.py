from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connection, transaction

from general.utils.otp import generate_otp, generate_user_token, verify_otp
from general.utils.gmail_sender import GmailSender
from django.contrib.auth.hashers import make_password
from users.models import UserAccount
from users.serializers import RequestOTPSerializer, VerifyOtpRequestSerializer, RequestLoginOTPSerializer
from ticket.models import Wallet

import uuid

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
            """
            with transaction.atomic():
                user = UserAccount.objects.create(
                    email = email,
                    is_superuser = False,
                    is_company_owner = False,
                    is_staff = False
                )
                Wallet.objects.create(
                    balance = 0,
                    user = user
                )"""
            unusable_password = make_password(None)
            user_id = str(uuid.uuid4())
            wallet_id = str(uuid.uuid4())

            with transaction.atomic():

                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO users_useraccount (id, email, password, is_superuser, is_company_owner, is_staff)
                        VALUES (%s, %s, %s, FALSE, FALSE, FALSE)
                        RETURNING id;
                    """, [user_id, email, unusable_password])
                    user_id = cursor.fetchone()[0]

                    cursor.execute("""
                        INSERT INTO ticket_wallet (balance, user_id, id)
                        VALUES (0, %s, %s);
                    """, [user_id, wallet_id])

            token = generate_user_token(email)

            return Response(data={'token': token}, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "Invalid code"}, status=status.HTTP_401_UNAUTHORIZED)

class LoginOTPView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = RequestLoginOTPSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        try:
            verification_code = generate_otp(user.email)
                
            gmail_sender = GmailSender()    
                
            gmail_sender.send(
                dest_gmail_address=user.email,
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
            
            return Response(data={"message": "OTP sent."}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

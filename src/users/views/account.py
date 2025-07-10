from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.conf import settings
from django.contrib.auth import authenticate
from users.serializers import ActivateAccountSerializer, CompanyOwnerWriteSerializer, LoginSerializer
from users.models import UserAccount
from users.exceptions import AuthenticationFailed
from users.serializers import AccountSerializer
from general.utils.otp import generate_otp, generate_user_token, verify_otp
from general.utils.gmail_sender import GmailSender


class CustomProviderAuthView(ProviderAuthView):

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 201:
            access_token = response.data['access']
            refresh_token = response.data['refresh']
            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                domain=settings.AUTH_COOKIE_DOMAIN,
                httponly=settings.AUTH_COOKIE_HTTPONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                domain=settings.AUTH_COOKIE_DOMAIN,
                httponly=settings.AUTH_COOKIE_HTTPONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        password = serializer.validated_data.get('password', None)
        
        if serializer.validated_data['type'] == 'password':
            user = authenticate(request, username=user.username, password=password)
            if not user:
                raise AuthenticationFailed
        else:
            if not verify_otp(user.email, serializer.validated_data['otp']):
                raise AuthenticationFailed

        refresh = RefreshToken.for_user(user)
        response = Response({
        'access': str(refresh.access_token),
            'refresh': str(refresh)
        })

        response.set_cookie(
            'access',
            str(refresh.access_token),
            max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
            path=settings.AUTH_COOKIE_PATH,
            secure=settings.AUTH_COOKIE_SECURE,
            domain=settings.AUTH_COOKIE_DOMAIN,
            httponly=settings.AUTH_COOKIE_HTTPONLY,
            samesite=settings.AUTH_COOKIE_SAMESITE
        )
        response.set_cookie(
            'refresh',
            str(refresh),
            max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
            path=settings.AUTH_COOKIE_PATH,
            secure=settings.AUTH_COOKIE_SECURE,
            domain=settings.AUTH_COOKIE_DOMAIN,
            httponly=settings.AUTH_COOKIE_HTTPONLY,
            samesite=settings.AUTH_COOKIE_SAMESITE
        )

        return response
        



class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')
        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data['access']
            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                domain=settings.AUTH_COOKIE_DOMAIN,
                httponly=settings.AUTH_COOKIE_HTTPONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
        return response


class CustomTokenVerifyView(TokenVerifyView):

    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')
        if access_token:
            request.data['token'] = access_token
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):

    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response
    

class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ActivateAccountSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(status=status.HTTP_200_OK)


class AdminCompanyOwner(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = CompanyOwnerWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)
    
class AdminGetAccounts(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(AccountSerializer(UserAccount.objects.filter(is_staff=False, is_superuser=False, is_company_owner=False), many=True).data, status=status.HTTP_200_OK)
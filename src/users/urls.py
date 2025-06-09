from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('otp/', OTPView.as_view()),
    path('otp/login/', LoginOTPView.as_view()),
    path('activate/', ActivateAccountView.as_view()),
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('admin/company-owner/', AdminCompanyOwner.as_view()),
    path('profile/', ProfileView.as_view())
]

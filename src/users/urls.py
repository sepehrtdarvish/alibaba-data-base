from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('otp/', OTPView.as_view()),
]

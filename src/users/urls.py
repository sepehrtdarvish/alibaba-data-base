from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('request-otp/', OTPView.as_view()),
]

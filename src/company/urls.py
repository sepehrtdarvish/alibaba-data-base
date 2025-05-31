from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('vehicle/train/', TrainView.as_view()),
    path('vehicle/', VehicleView.as_view()),
    path('policy/', CompanyPolicyView.as_view())
]

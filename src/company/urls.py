from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('vehicle/', VehicleView.as_view()),
    path('vehicle/company/', CompanyVehicleView.as_view()),
    path('policy/', CompanyPolicyView.as_view()),
    path('report/', ReportView.as_view()),
    path('report/company/', ReportCompanyView.as_view(),)
]

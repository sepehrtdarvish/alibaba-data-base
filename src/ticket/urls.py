from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('company/ticket/', CompanyOwnerTicketView.as_view()),
    path('company/', CompanyView.as_view()),
    path('location/', LocationView.as_view()),
    path('location/admin/', AdminLocationView.as_view()),
    path('', TicketView.as_view()),
    path('reserve/', ReservationView.as_view()),
    path('reserve/payment/', CompleteReservationView.as_view()),
    path('reserve/cancel/<str:reservation_id>/', CancelReservationView.as_view()),
    path('wallet/', WalletView.as_view())
]

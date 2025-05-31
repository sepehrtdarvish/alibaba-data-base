from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone


from ticket.models import StationLocation, LocationType, Ticket, Reservation
from ticket.serializers import GetLocationSerializer, TicketQuerySerializer, ReservationModelSerializer, ReservationWriteSerializer

from company.models import RefundRule
from users.decorators import company_required

from django.conf import settings


class ReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReservationWriteSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)
    
    def get(self, request):
        user = request.user
        reservations = Reservation.objects.filter(user=user)

        return Response(ReservationModelSerializer(reservations, many=True).data, status=status.HTTP_200_OK)
    
    
class CancelReservationView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, reservation_id):

        reservation = Reservation.objects.filter(id=reservation_id, user=request.user).first()
        company = reservation.ticket_section.section.vehicle.company
        refund_policy = RefundPolicy.objects.filter(company=company).first()
        ticket_start_date = reservation.ticket_section.ticket.start_at
        today_date = timezone.now()
        remain_days = (ticket_start_date - today_date).days

        refund_rules = refund_policy.rules.filter(days__lte=remain_days).order_by('-days').first()
        refund_percentage = refund_rules.refund_percentage

        refund_amount = reservation.ticket_section.price * refund_percentage / 100

        return Response({'refund_amount': refund_amount}, status=status.HTTP_200_OK)


    def post(self, request, reservation_id):
        reservation = Reservation.objects.get(id=reservation_id, user=request.user)
        reservation.delete()

        return Response(status=status.HTTP_200_OK)

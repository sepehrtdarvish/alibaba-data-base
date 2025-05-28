from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.db.models import Q


from ticket.models import StationLocation, LocationType, Ticket, Reservation
from ticket.serializers import GetLocationSerializer, TicketQuerySerializer, ReservationModelSerializer, ReservationWriteSerializer
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
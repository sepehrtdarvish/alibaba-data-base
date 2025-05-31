from rest_framework import serializers
from ticket.models import StationLocation, LocationType, Ticket, Reservation
from company.models import Vehicle, Section, VehicleTypes, TrainServices, Train, Bus, AirPlane, BusServices, AirplaneServices, ReportType

from django.db import transaction

class ReportWriteSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=1000)
    subject = serializers.ChoiceField(choices=ReportType.choices)
    reservation = serializers.PrimaryKeyRelatedField(
        queryset = Reservation.objects.all(), required=False
    )
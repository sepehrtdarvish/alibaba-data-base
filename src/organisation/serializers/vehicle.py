from rest_framework import serializers
from ticket.models import StationLocation, LocationType, TicketType, Ticket
from organisation.models import Vehicle, Company, VehicleTypes


class VehicleWriteSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=VehicleTypes.choices, required=True)
    
from rest_framework import serializers
from ticket.models import StationLocation, LocationType, TicketType, Ticket
from organisation.models import Vehicle, Company, VehicleTypes, TrainServices, Train

from django.db import transaction

class TrainWriteSerializer(serializers.Serializer):
    capacity = serializers.IntegerField(required=True)
    star_number = serializers.IntegerField(required=True)
    flatbed_wagon = serializers.BooleanField(required=False)
    air_conditioning = serializers.BooleanField(required=False)
    television = serializers.BooleanField(required=False)
    unicode = serializers.CharField(required=True)


    def validate_capacity(self, obj):
        if obj > 1000 or obj < 20:
            raise serializers.ValidationError("Invalid Capacity")
        
    def validate_star_number(self, obj):
        if obj > 5 or obj < 0:
            raise serializers.ValidationError("Invalid start number")
        
    def create(self, validated_data):
        with transaction.atomic():
            services = TrainServices.objects.create(
                flatbed_wagon = validated_data.get('flatbed_wagon', None),
                air_conditioning = validated_data.get('air_conditioning', None),
                television = validated_data.get('television', None)
            )

            train = Train.objects.create(
                capacity = validated_data['capacity'],
                unicode = validated_data['unicode'],
                star_number = validated_data['star_number'],
                services = services
            )

            return train
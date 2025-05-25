from rest_framework import serializers
from ticket.models import StationLocation, LocationType, TicketType, Ticket
from organisation.models import Vehicle, Company

class GetLocationSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=LocationType.choices)


class StationLocationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationLocation
        fields = '__all__'


class TicketWriteSerializer(serializers.Serializer):
    origin = serializers.PrimaryKeyRelatedField(
        queryset = StationLocation.objects.all(), required=True
    )
    destination = serializers.PrimaryKeyRelatedField(
        queryset = StationLocation.objects.all(), required=True
    )
    price = serializers.FloatField(required=True)
    start_at = serializers.DateTimeField(required=True)
    duration = serializers.DurationField(required=True)
    class_type = serializers.ChoiceField(choices=TicketType.choices, required=True)
    capacity = serializers.IntegerField(required=True)
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset = Vehicle.objects.all(), required=True
    )
    stops = serializers.IntegerField(required=False, allow_null=True)


    def validate_vehicle(self, obj):
        company = self.context['company']
        if obj.company != company:
            raise serializers.ValidationError('Vehicle does not belong to company.')
        return obj
    
    def validate(self, attrs):
        # Validate locations
        if attrs['origin'] == attrs['destination']:
            raise serializers.ValidationError('Origin and destination cannot be the same.')

        return attrs
    
    def create(self, validated_data):
        return Ticket.objects.create(**validated_data)
    

class TicketModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

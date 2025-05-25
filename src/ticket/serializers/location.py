from rest_framework import serializers
from ticket.models import StationLocation, LocationType, TicketType, Ticket
from organisation.models import Vehicle, Company

class StationLocationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationLocation
        fields = '__all__'

class StationLocationSerializer(serializers.Serializer):
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=LocationType.choices, required=True)
    name = serializers.CharField(required=True)

    def validate(self, attrs):
        if StationLocation.objects.filter(
            name = attrs['name'],
            type = attrs['type'],
            country = attrs['country'],
            city = attrs['city']
        ).exists():
            raise serializers.ValidationError('duplicate station')
        
        return attrs
    

    def create(self, validated_data):
        return StationLocation.objects.create(**validated_data)
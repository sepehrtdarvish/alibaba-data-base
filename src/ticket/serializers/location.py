from rest_framework import serializers
from ticket.models import StationLocation, LocationType, Ticket
from company.models import Vehicle, Company
from django.db import connection

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
        """
        if StationLocation.objects.filter(
            name = attrs['name'],
            type = attrs['type'],
            country = attrs['country'],
            city = attrs['city']
        ).exists():
            raise serializers.ValidationError('duplicate station')
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM ticket_stationlocation
                WHERE name = %s AND type = %s AND country = %s AND city = %s
                LIMIT 1;
            """, [attrs['name'], attrs['type'], attrs['country'], attrs['city']])
            
            if cursor.fetchone():
                raise serializers.ValidationError('duplicate station')
        
        return attrs
    

    def create(self, validated_data):
        return StationLocation.objects.create(**validated_data)
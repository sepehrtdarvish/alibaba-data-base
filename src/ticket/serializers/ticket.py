from rest_framework import serializers
from ticket.models import StationLocation, LocationType, TicketType, Ticket, TicketSection
from organisation.models import Vehicle, Company, Section

class GetLocationSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=LocationType.choices)


class StationLocationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationLocation
        fields = '__all__'


class TicketSectionSerializer(serializers.Serializer):
    section = serializers.PrimaryKeyRelatedField(
        queryset = Section.objects.all(), required=True
    )
    price = serializers.FloatField(required=True)
 

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
    sections = TicketSectionSerializer(required=True, many=True)
    stops = serializers.IntegerField(required=True, allow_null=True)


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
        sections = validated_data['sections']

        ticket = Ticket.objects.create(
            origin = validated_data['origin'],
            destination = validated_data['destination'],
            price = validated_data['price'],
            start_at = validated_data['start_at'],
            duration = validated_data['duration'],
            class_type = validated_data['class_type'],
            capacity = validated_data['capacity'],
            stops = validated_data['stops'],
        )

        for section in sections:
            TicketSection.objects.create(
                ticket = ticket,
                section = section['section'],
                price = section['price']
            )

        return ticket


class TicketModelSerializer(serializers.ModelSerializer):
    sections = TicketSectionSerializer(many=True)

    class Meta:
        model = Ticket
        fields = '__all__'


class TicketSectionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketSection
        fields = '__all__'
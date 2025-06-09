from rest_framework import serializers
from ticket.models import StationLocation, LocationType, Ticket, TicketSection
from company.models import Vehicle, Company, Section, SectionType, Train, Bus, AirPlane, RefundRule
from company.serializers import TrainReadSerializer, BusReadSerializer, AirplaneReadSerializer, SectionReadSerializer

from django.db import transaction


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
 


class TicketSectionReadSerializer(serializers.ModelSerializer):
    section = SectionReadSerializer()
    
    class Meta:
        model = TicketSection
        fields = '__all__'


class TicketWriteSerializer(serializers.Serializer):
    origin = serializers.PrimaryKeyRelatedField(
        queryset = StationLocation.objects.all(), required=True
    )
    destination = serializers.PrimaryKeyRelatedField(
        queryset = StationLocation.objects.all(), required=True
    )
    start_at = serializers.DateTimeField(required=True)
    duration = serializers.DurationField(required=True)
    sections = TicketSectionSerializer(required=True, many=True)
    stops = serializers.IntegerField(required=True, allow_null=True)


    def validate_vehicle(self, obj):
        company = self.context['company']
        if obj.company != company:
            raise serializers.ValidationError('Vehicle does not belong to company.')
        return obj
    
    def validate(self, attrs):
        # Validate Company
        company = self.context['company']
        refund = RefundRule.objects.filter(company=company).first()
        if not refund:
            raise serializers.ValidationError('Company does not have a refund policy yet.')
        
        # Validate locations
        if attrs['origin'] == attrs['destination']:
            raise serializers.ValidationError('Origin and destination cannot be the same.')
        
        sections = attrs['sections']
        vehicle = sections[0]['section'].vehicle

        for section in sections:
            if section['section'].vehicle != vehicle:
                raise serializers.ValidationError('All sections must belong to the same vehicle.')
            
        if vehicle.company != self.context['company']:
            raise serializers.ValidationError('Vehicle does not belong to company.')
            
        
        return attrs
    
    def create(self, validated_data):
        sections = validated_data['sections']

        with transaction.atomic():
            ticket = Ticket.objects.create(
                origin = validated_data['origin'],
                destination = validated_data['destination'],
                start_at = validated_data['start_at'],
                duration = validated_data['duration'],
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
    sections = TicketSectionReadSerializer(many=True)
    origin = StationLocationModelSerializer(read_only=True)
    destination = StationLocationModelSerializer(read_only=True)
    vehicle = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'

    def get_vehicle(self, obj):
        vehicle = obj.sections.first().section.vehicle
        
        if hasattr(vehicle, 'train'):
            train = vehicle.train
            return TrainReadSerializer(train).data
        elif hasattr(vehicle, 'bus'):
            bus = vehicle.bus
            return BusReadSerializer(bus).data
        elif hasattr(vehicle, 'airplane'):
            airplane = vehicle.airplane
            return AirplaneReadSerializer(airplane).data


class TicketSectionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketSection
        fields = '__all__'


class TicketQuerySerializer(serializers.Serializer):
    origin = serializers.PrimaryKeyRelatedField(
        queryset = StationLocation.objects.all(), required=False
    )
    destination = serializers.PrimaryKeyRelatedField(
        queryset = StationLocation.objects.all(), required=False
    )
    start_at = serializers.DateField(required=False)
    min_price = serializers.FloatField(required=False)
    max_price = serializers.FloatField(required=False)
    class_type = serializers.ChoiceField(choices=SectionType.choices, required=False)
    company = serializers.PrimaryKeyRelatedField(
        queryset = Company.objects.all(), required=False
    )
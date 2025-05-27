from rest_framework import serializers
from ticket.models import StationLocation, LocationType, Ticket
from organisation.models import Vehicle, Section, VehicleTypes, TrainServices, Train, Bus, AirPlane, BusServices, AirplaneServices

from django.db import transaction


class SeatWriteSerializer(serializers.Serializer):
    start_number = serializers.IntegerField(required=True)
    end_number = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['start_number'] > attrs['end_number']:
            raise serializers.ValidationError('Start number cannot be greater than end number.')

        return attrs

    def create(self, attrs):
        return Section.objects.create(
            start_number = attrs['start_number'],
            end_number = attrs['end_number'],
            name = attrs['name'],
            vehicle = self.context['vehicle']
        )


class TrainWriteSerializer(serializers.Serializer):
    capacity = serializers.IntegerField(required=True)
    star_number = serializers.IntegerField(required=True)
    flatbed_wagon = serializers.BooleanField(required=True)
    air_conditioning = serializers.BooleanField(required=True)
    television = serializers.BooleanField(required=True)
    unicode = serializers.CharField(required=True)
    catering_service = serializers.BooleanField(required=True)
    wifi_access = serializers.BooleanField(required=True)
    sections = SeatWriteSerializer(many=True, required=True)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request_data = kwargs.get('data', {})

        capacity = request_data.get('capacity')

        self.context['capacity'] = capacity

        self.fields['sections'].context.update({'capacity': capacity})



    def validate_capacity(self, obj):
        if obj > 1000 or obj < 20:
            raise serializers.ValidationError("Invalid Capacity")
        
        return obj
        
    def validate_star_number(self, obj):
        if obj > 5 or obj < 0:
            raise serializers.ValidationError("Invalid start number")

        return obj


    def validate(self, attrs):
        capacity = attrs['capacity']
        sections_lst = attrs['sections']
        if len(sections_lst) < 1:
            raise serializers.ValidationError("Invalid section number")
        sections_capacity = 0
        for section in sections_lst:
            sections_capacity += section['end_number'] - section['start_number'] + 1

        if capacity != sections_capacity:
            raise serializers.ValidationError("Invalid Seats number")

        return attrs
    
    
    def create(self, validated_data):
        with transaction.atomic():
            services = TrainServices.objects.create(
                flatbed_wagon = validated_data.get('flatbed_wagon', None),
                air_conditioning = validated_data.get('air_conditioning', None),
                television = validated_data.get('television', None),
                catering_service = validated_data.get('catering_service', False),
                wifi_access = validated_data.get('wifi_access', False),
            )


            train = Train.objects.create(
                capacity = validated_data['capacity'],
                unicode = validated_data['unicode'],
                star_number = validated_data['star_number'],
                services = services,
                company=self.context['company']
            )


            sections = validated_data['sections']
            sections_serializer = SeatWriteSerializer(data=sections, many=True, context={'vehicle': train})
            sections_serializer.is_valid(raise_exception=True)
            sections_serializer.save()


        return train


class SectionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'start_number', 'end_number', 'name']


class TrainServicesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainServices
        fields = [
            'id',
            'catering_service',
            'wifi_access',
            'flatbed_wagon',
            'air_conditioning',
            'television'
        ]        

class TrainReadSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    sections = SectionReadSerializer(many=True, read_only=True)

    class Meta:
        model = Train
        fields = '__all__'

    def get_services(self, obj):
        train_services = TrainServices.objects.filter(id=obj.services.id).first()
        return TrainServicesReadSerializer(train_services).data


class BusServicesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusServices
        fields = [
            'id',
            'catering_service',
            'wifi_access',
            'individual_screen',
            'air_conditioning'
        ]        

class BusReadSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    
    class Meta:
        model = Bus
        fields = '__all__'

    def get_services(self, obj):
        bus_services = BusServices.objects.filter(id=obj.services.id).first()
        return BusServicesReadSerializer(bus_services).data
    

class AirplaneServicesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusServices
        fields = [
            'id',
            'catering_service',
            'wifi_access',
            'bendable_seats'
        ]    


class AirplaneReadSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    
    class Meta:
        model = AirPlane
        fields = '__all__'

    def get_services(self, obj):
        airplane_services = AirplaneServices.objects.filter(id=obj.services.id).first()
        return AirplaneServicesReadSerializer(airplane_services).data
    


class GetVehicleSerializer(serializers.Serializer):
    id = serializers.UUIDField(required = False)
    type = serializers.ChoiceField(choices=VehicleTypes.choices, required=True)


    def validate(self, attrs):
        type = attrs.get('type')
        id = attrs.get('id', None)

        attrs['vehicle_model'], attrs['vehicle_read_serializer'] = self.get_vehicle_type(type=type)

        if id:
            vehicle = attrs['vehicle_model'].objects.filter(id=id).first()
            if vehicle:
                attrs['vehicle'] = vehicle
            else:
                raise serializers.ValidationError("There is no vehicle with the given ID.")
            
        return attrs
    
    def get_vehicle_type(self, type):
        if type == VehicleTypes.Train:
            return Train, TrainReadSerializer
        elif type == VehicleTypes.Bus:
            return Bus, BusReadSerializer
        elif type == VehicleTypes.AirPlane:
            return AirPlane, AirplaneReadSerializer
from rest_framework import serializers
from company.models import Vehicle, Section, VehicleTypes

from django.db import transaction, connection
from company.models import VehicleTypes
import uuid

class SeatWriteSerializer(serializers.Serializer):
    start_number = serializers.IntegerField(required=True)
    end_number = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['start_number'] > attrs['end_number']:
            raise serializers.ValidationError('Start number cannot be greater than end number.')

        return attrs

    def create(self, validated_data):
        return Section.objects.create(
            start_number = validated_data['start_number'],
            end_number = validated_data['end_number'],
            name = validated_data['name'],
            vehicle = self.context['vehicle']
        )


class VehicleWriteSerializer(serializers.Serializer):
    capacity = serializers.IntegerField(required=False)
    television = serializers.BooleanField(required=False)
    unicode = serializers.CharField(required=False)
    catering_service = serializers.BooleanField(required=False)
    wifi_access = serializers.BooleanField(required=False)
    sections = SeatWriteSerializer(many=True, required=True)
    unicode = serializers.CharField(required=True)
    vehicle_type = serializers.ChoiceField(choices=VehicleTypes.choices)


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
        vehicle_id = uuid.uuid4()
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO company_vehicle (id, air_conditioning, television, catering_service, wifi_access, vehicle_type, capacity, unicode, company_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, [
                    str(vehicle_id),
                    validated_data.get('air_conditioning', False),
                    validated_data.get('television', False),
                    validated_data.get('catering_service', False),
                    validated_data.get('wifi_access', False),
                    validated_data.get('vehicle_type'),
                    validated_data['capacity'],
                    validated_data['unicode'],
                    self.context['company'].id
                ])
                vehicle_id = cursor.fetchone()[0]

            sections = validated_data['sections']
            created_sections = []

            for section in sections:
                new_section_id = uuid.uuid4()

                start_number = section['start_number']
                end_number = section['end_number']
                name = section['name']

                if start_number > end_number:
                    raise ValueError('Start number cannot be greater than end number.')

                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO company_section (id, start_number, end_number, name, vehicle_id)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING *;
                    """, [
                        str(new_section_id),
                        start_number,
                        end_number,
                        name,
                        vehicle_id
                    ])
                    columns = [col[0] for col in cursor.description]
                    row = cursor.fetchone()
                    created_sections.append(dict(zip(columns, row)))

        return {
            'id': vehicle_id,
            'capacity': validated_data['capacity'],
            'unicode': validated_data['unicode'],
            'company_id': self.context['company'].id,
            'sections': created_sections,
            'vehicle_type': validated_data['vehicle_type'],
            'television': validated_data.get('television', False),
            'catering_service': validated_data.get('catering_service', False),
            'wifi_access': validated_data.get('wifi_access', False),
            'air_conditioning': validated_data.get('air_conditioning', False),
        }


class SectionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'start_number', 'end_number', 'name']



class VehicleReadSerializer(serializers.ModelSerializer):
    sections = SectionReadSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'



class GetVehicleSerializer(serializers.Serializer):
    id = serializers.UUIDField(required = False)
    type = serializers.ChoiceField(choices=VehicleTypes.choices, required=True)


    def validate(self, attrs):
        type = attrs.get('type')
        id = attrs.get('id', None)


        if id:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM company_vehicle
                    WHERE id = %s
                    LIMIT 1;
                """, [id])
                row = cursor.fetchone()

            if row:
                columns = [col[0] for col in cursor.description]
                vehicle = dict(zip(columns, row))
                attrs['vehicle'] = vehicle
            else:
                raise serializers.ValidationError("There is no vehicle with the given ID.")
        
        return attrs

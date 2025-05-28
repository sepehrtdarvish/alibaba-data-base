from rest_framework import serializers
from ticket.models import StationLocation, LocationType, Ticket, TicketSection, Reservation
from organisation.models import Vehicle, Company, Section, SectionType, Train, Bus, AirPlane
from organisation.serializers import TrainReadSerializer, BusReadSerializer, AirplaneReadSerializer, SectionReadSerializer

class ReservationWriteSerializer(serializers.Serializer):
    ticket_section = serializers.PrimaryKeyRelatedField(
        queryset = TicketSection.objects.all(), required=True
    )


    def validate(self, attrs):
        section = attrs['ticket_section'].section
        seats_reserved = Reservation.objects.filter(ticket_section=attrs['ticket_section']).count()
        
        if section.end_number - section.start_number + 1 == seats_reserved:
            raise serializers.ValidationError('Section Capacity is full.')
        
        else:
            seat_num = seats_reserved + 1

        attrs['seat_num'] = seat_num

        return attrs
    

    def create(self, validated_data):
        reservation = Reservation.objects.create(
            ticket_section = validated_data['ticket_section'],
            seat_number = validated_data['seat_num'],
            user = self.context['user']
            )

        return reservation
    

class ReservationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
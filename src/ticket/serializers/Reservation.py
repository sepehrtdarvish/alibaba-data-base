from rest_framework import serializers
from django.core.cache import cache
import uuid


from ticket.models import TicketSection, Reservation
from ticket.serializers import TicketSectionModelSerializer

from ticket.utils import get_reserved_seats, find_seat_number, reserve_ticket

class ReservationWriteSerializer(serializers.Serializer):
    ticket_section = serializers.PrimaryKeyRelatedField(
        queryset = TicketSection.objects.all(), required=True
    )


    def validate(self, attrs):
        user = self.context['user']
        ticket_section = attrs['ticket_section']

        user_reserving = Reservation.objects.filter(ticket_section=ticket_section, user=user).count()
        if user_reserving != 0:
            raise serializers.ValidationError('You have already reserved a seat in this section.')

        cached_seats = get_reserved_seats(ticket_section_id=ticket_section.id)

        reservations = Reservation.objects.filter(ticket_section=attrs['ticket_section'])
        reserved_seats_db = [reservation.seat_number for reservation in reservations]

        reserved_seats = set(map(int, reserved_seats_db)) | set(map(int, cached_seats))

        new_seat_number = find_seat_number(capacity=ticket_section.section.capacity, reserved_seats=reserved_seats)
        if not new_seat_number:
            raise serializers.ValidationError('Capacity Full!')

        attrs['seat_number'] = new_seat_number
        attrs['user'] = user

        return attrs
    

    def create(self, validated_data):
        payment_token = uuid.uuid4().hex
        reserve_ticket(
            payment_token=payment_token,
            user_id=validated_data['user'].id,
            ticket_section_id=validated_data['ticket_section_id'],
            seat_number=validated_data['seat_number'],
        )

        return payment_token


class ReservationReadSerializer(serializers.ModelSerializer):
    ticket_section = TicketSectionModelSerializer()

    class Meta:
        model = Reservation
        fields = '__all__'


class ReservationGetIDSerializezr(serializers.Serializer):
    reservation = serializers.PrimaryKeyRelatedField(
        queryset = Reservation.objects.all(), required=True
    )

    def validate_reservartion(self, obj):
        if obj.user != self.context['user']:
            raise serializers.ValidationError('This reservation does not belong to this user.')
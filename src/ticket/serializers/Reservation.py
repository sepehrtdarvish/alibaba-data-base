from rest_framework import serializers
from django.core.cache import cache
from django.db import transaction, connection

import uuid

from users.models import UserAccount

from ticket.models import TicketSection, Reservation, Transaction, TransactionType
from ticket.serializers import TicketSectionModelSerializer
from ticket.utils import get_reserved_seats, find_seat_number, reserve_ticket

class ReservationWriteSerializer(serializers.Serializer):
    ticket_section = serializers.PrimaryKeyRelatedField(
        queryset = TicketSection.objects.all(), required=True
    )


    def validate(self, attrs):
        user = self.context['user']
        ticket_section = attrs['ticket_section']

        """user_reserving = Reservation.objects.filter(ticket_section=ticket_section, user=user).count()"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM ticket_reservation
                WHERE ticket_section_id = %s AND user_id = %s;
            """, [ticket_section.id, user.id])
            user_reserving = cursor.fetchone()[0]

        if user_reserving != 0:
            raise serializers.ValidationError('You have already reserved a seat in this section.')

        cached_seats = get_reserved_seats(ticket_section_id=ticket_section.id)

        """reservations = Reservation.objects.filter(ticket_section=attrs['ticket_section'])
        reserved_seats_db = [reservation.seat_number for reservation in reservations]"""

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT seat_number FROM ticket_reservation
                WHERE ticket_section_id = %s;
            """, [ticket_section.id])
            reserved_seats_db = [row[0] for row in cursor.fetchall()]

        reserved_seats = set(map(int, reserved_seats_db)) | set(map(int, cached_seats))
        
        new_seat_number = find_seat_number(
            capacity=ticket_section.section.end_number - ticket_section.section.start_number + 1,
            reserved_seats=list(reserved_seats)
            )
        if not new_seat_number:
            raise serializers.ValidationError('Capacity Full!')

        attrs['seat_number'] = new_seat_number
        attrs['user'] = user

        return attrs
    

    def create(self, validated_data):
        payment_token = str(uuid.uuid4())

        reserve_ticket(
            payment_token=payment_token,
            user_id=validated_data['user'].id,
            ticket_section_id=validated_data['ticket_section'].id,
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
        

class CompleteResrvationSerializer(serializers.Serializer):
    payment_token = serializers.UUIDField(required=True)

    def validate(self, attrs):
        payment_token = attrs['payment_token']

        reservation = cache.get(f'r_token_{payment_token}')
        if reservation:
            attrs['reservation'] = reservation
        else:
            raise serializers.ValidationError('No reservation found!')

        # user = UserAccount.objects.filter(id=reservation['user_id']).first()
        # ticket_section = TicketSection.objects.filter(id=reservation['ticket_section_id']).first()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users_useraccount WHERE id = %s LIMIT 1;", [reservation['user_id']])
            columns = [col[0] for col in cursor.description]
            user_row = cursor.fetchone()
        user = dict(zip(columns, user_row)) if user_row else None

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM ticket_ticketsection WHERE id = %s LIMIT 1;", [reservation['ticket_section_id']])
            columns = [col[0] for col in cursor.description]
            ticket_section_row = cursor.fetchone()
        ticket_section = dict(zip(columns, ticket_section_row)) if ticket_section_row else None


        if not user or not ticket_section:
            raise serializers.ValidationError('Invalid reservation data.')

        with connection.cursor() as cursor:
            cursor.execute("SELECT balance FROM ticket_wallet WHERE user_id = %s LIMIT 1;", [reservation['user_id']])
            row = cursor.fetchone()
        balance = row[0] if row else 0

        if ticket_section['price'] > balance:
            raise serializers.ValidationError('Wallet balance not enough.')

        attrs['user'] = user
        attrs['ticket_section'] = ticket_section
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM ticket_wallet WHERE user_id = %s LIMIT 1;
                """, [validated_data['user']['id']])
                row = cursor.fetchone()
            if not row:
                raise serializers.ValidationError('Wallet not found for user.')
            wallet_id = row[0]
            # new_transaction = Transaction.objects.create(
            #     amount = validated_data['ticket_section'].price,
            #     wallet = validated_data['user'].wallet,
            #     type = TransactionType.WITHDRAWAL
            # )
            transaction_id = uuid.uuid4()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ticket_transaction (id, amount, wallet_id, type, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    RETURNING id;
                """, [
                    transaction_id,
                    validated_data['ticket_section']['price'],
                    wallet_id,
                    'WITHDRAWAL'
                ])
                transaction_id = cursor.fetchone()[0]

            # reservation = Reservation.objects.create(
            #     user = validated_data['user'],
            #     ticket_section = validated_data['ticket_section'],
            #     seat_number = validated_data['reservation']['seat_number'],
            #     transaction = new_transaction
            # )


            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ticket_wallet
                    SET balance = balance - %s
                    WHERE id = %s;
                """, [validated_data['ticket_section']['price'], wallet_id])
                
            reservation_id = uuid.uuid4()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ticket_reservation (id, user_id, ticket_section_id, seat_number, transaction_id, created_at, is_cancelled)
                    VALUES (%s, %s, %s, %s, %s, Now(), %s)
                    RETURNING *;
                """, [
                    reservation_id,
                    validated_data['user']['id'],
                    validated_data['ticket_section']['id'],
                    validated_data['reservation']['seat_number'],
                    transaction_id,
                    False
                ])
                columns = [col[0] for col in cursor.description]
                reservation_row = cursor.fetchone()

        return Reservation.objects.get(id=reservation_id)

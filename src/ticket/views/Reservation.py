from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone
from django.db import transaction, connection
import uuid
from ticket.utils import get_refund_amount
from ticket.models import StationLocation, LocationType, Ticket, Reservation
from ticket.serializers import CompleteResrvationSerializer, ReservationGetIDSerializezr, ReservationReadSerializer, ReservationWriteSerializer

from company.models import RefundRule

from users.decorators import company_required

from ticket.models import Transaction, TransactionType

from django.conf import settings


class ReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReservationWriteSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        payment_token = serializer.save()

        return Response({'token': payment_token}, status=status.HTTP_200_OK)
    
    def get(self, request):
        user = request.user

        # reservations = Reservation.objects.filter(user=user)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM ticket_reservation
                WHERE user_id = %s;
            """, [user.id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        ids = [row[0] for row in rows]
        reservations = Reservation.objects.filter(id__in=ids)

        return Response(ReservationReadSerializer(reservations, many=True).data, status=status.HTTP_200_OK)
    
    
class CancelReservationView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, reservation_id):
        serializer = ReservationGetIDSerializezr(data={'reservation': reservation_id}, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        reservation = serializer.validated_data['reservation']

        refund_amount = get_refund_amount(reservation=reservation)
    
        return Response({'refund_amount': refund_amount}, status=status.HTTP_200_OK)


    def post(self, request, reservation_id):
        user = request.user

        serializer = ReservationGetIDSerializezr(data={'reservation': reservation_id}, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        reservation = serializer.validated_data['reservation']

        with transaction.atomic():
            # reservation.is_cancelled = True
            # reservation.save()
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ticket_reservation
                    SET is_cancelled = TRUE
                    WHERE id = %s;
                """, [reservation_id])

            refund_amount = get_refund_amount(reservation=reservation)

            # user.wallet.balance += refund_amount
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ticket_wallet
                    SET balance = balance + %s
                    WHERE id = %s;
                """, [refund_amount, user.wallet.id])

            # Transaction.objects.create(
            #     type = TransactionType.REFUND,
            #     amount = refund_amount,
            #     wallet = user.wallet
            # )
            transaction_id = uuid.uuid4()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ticket_transaction (id, type, amount, wallet_id, created_at)
                    VALUES (%s, %s, %s, %s, NOW());
                """, [transaction_id, 'REFUND', refund_amount, user.wallet.id])

        return Response(status=status.HTTP_200_OK)


class CompleteReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompleteResrvationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()

        return Response(ReservationReadSerializer(reservation).data, status=status.HTTP_200_OK)
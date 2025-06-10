from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone
from django.db import transaction

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
        reservations = Reservation.objects.filter(user=user)

        return Response(ReservationReadSerializer(reservations, many=True).data, status=status.HTTP_200_OK)
    
    
class CancelReservationView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, reservation_id):
        serializer = ReservationGetIDSerializezr(data={'reservation': reservation_id}, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        reservation = serializer.validated_data['reservation']

        refund_amount = get_refund_amount(reservation=reservation)
        
        # TODO Check logic again with validated timezone


        return Response({'refund_amount': refund_amount}, status=status.HTTP_200_OK)


    def post(self, request, reservation_id):
        user = request.user

        serializer = ReservationGetIDSerializezr(data={'reservation': reservation_id}, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        reservation = serializer.validated_data['reservation']

        with transaction.atomic():
            reservation.is_cancelled = True
            reservation.save()
        
            refund_amount = get_refund_amount(reservation=reservation)
            user.wallet.balance += refund_amount

            Transaction.objects.create(
                type = TransactionType.REFUND,
                amount = refund_amount,
                wallet = user.wallet
            )

        return Response(status=status.HTTP_200_OK)


class CompleteReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompleteResrvationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()

        return Response(ReservationReadSerializer(reservation).data, status=status.HTTP_200_OK)
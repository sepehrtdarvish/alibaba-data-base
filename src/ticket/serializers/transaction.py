from rest_framework import serializers
from django.db import transaction, connection
from ticket.models import Transaction, TransactionType
import uuid

class WalletChargeSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True)

    def create(self, validated_data):
        user = self.context['user']
        amount = validated_data['amount']
        user_id = str(user.id)

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ticket_wallet
                    SET balance = balance + %s
                    WHERE user_id = %s
                    RETURNING id, balance;
                """, [amount, user_id])
                wallet_row = cursor.fetchone()

            if not wallet_row:
                raise serializers.ValidationError("Wallet not found.")

            wallet_id, new_balance = wallet_row

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ticket_transaction (id, type, amount, wallet_id, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, [uuid.uuid4(), 'deposit', amount, wallet_id])

        return {
            "wallet_id": wallet_id,
            "new_balance": new_balance
        }
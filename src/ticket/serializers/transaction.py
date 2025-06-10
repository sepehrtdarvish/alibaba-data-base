from rest_framework import serializers
from django.db import transaction


from ticket.models import Transaction, TransactionType
class WalletChargeSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True)

    def create(self, validated_data):
        user = self.context['user']
        wallet = user.wallet
        amount = validated_data['amount']


        with transaction.atomic():
            wallet.balance += amount
            wallet.save()

            Transaction.objects.create(
                type = TransactionType.DEPOSIT,
                amount = amount,
                wallet = wallet
            )

        return wallet
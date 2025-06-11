from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.db.models import Q

from ticket.serializers import WalletChargeSerializer

class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WalletChargeSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)   
        serializer.save()

        return Response(status=status.HTTP_200_OK)
    
    def get(self, request):
        balance = request.user.wallet.balance

        return Response(data={"balance": balance}, status=status.HTTP_200_OK)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.decorators import method_decorator
from users.decorators import company_required

from organisation.serializers import TrainWriteSerializer

class Train(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(company_required)
    def post(self, request):
        serializer = TrainWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        train = serializer.save()

        return Response(status=status.HTTP_200_OK)
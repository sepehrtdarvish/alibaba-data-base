from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.decorators import method_decorator
from users.decorators import company_required

from organisation.models import Train
from organisation.serializers import TrainWriteSerializer, GetVehicleSerializer, TrainReadSerializer

class TrainView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(company_required)
    def post(self, request):
        serializer = TrainWriteSerializer(data=request.data, context={'company': request.company})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

class VehicleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = GetVehicleSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        vehicle_model = serializer.validated_data['vehicle_model']
        vehicle_serializer = serializer.validated_data['vehicle_read_serializer']

        vehicle = serializer.validated_data.get('vehicle', None)

        if vehicle:
            return Response(vehicle_serializer(vehicle).data, status=status.HTTP_200_OK)
        else:
            return Response(vehicle_serializer(vehicle_model.objects.all(), many=True).data, status=status.HTTP_200_OK)

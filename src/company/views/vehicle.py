from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.decorators import method_decorator
from users.decorators import company_required

from company.serializers import VehicleWriteSerializer, GetVehicleSerializer, VehicleReadSerializer, GetCompanyVehicleSerializer
from company.models import Vehicle

class VehicleView(APIView):
    permission_classes = [IsAuthenticated]


    @method_decorator(company_required)
    def post(self, request):
        serializer = VehicleWriteSerializer(data=request.data, context={'company': request.company})
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()

        return Response(VehicleReadSerializer(vehicle).data ,status=status.HTTP_200_OK)


    def get(self, request):
        serializer = GetVehicleSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        vehicle = serializer.validated_data.get('vehicle', None)
        type = serializer.validated_data.get('type')

        if vehicle:
            return Response(VehicleReadSerializer(vehicle).data, status=status.HTTP_200_OK)
        else:
            return Response(VehicleReadSerializer(Vehicle.objects.filter(type=type), many=True).data, status=status.HTTP_200_OK)


class CompanyVehicleView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(company_required)
    def get(self, request):
        company = request.company

        serializer = GetCompanyVehicleSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        type = serializer.validated_data.get('type')


        return Response(VehicleReadSerializer(Vehicle.objects.filter(type=type, company=company), many=True).data, status=status.HTTP_200_OK)


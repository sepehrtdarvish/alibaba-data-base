from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.decorators import method_decorator
from django.db import connection
from ticket.models import StationLocation, LocationType
from ticket.serializers import GetLocationSerializer, StationLocationModelSerializer, StationLocationSerializer
from users.decorators import company_required

class LocationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = GetLocationSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        location_type = serializer.validated_data['type']
        """locations = StationLocation.objects.filter(type=location_type)"""

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM ticket_stationlocation
                WHERE type = %s;
            """, [location_type])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        locations = [dict(zip(columns, row)) for row in rows]

        location_serializer = StationLocationModelSerializer(locations, many=True)

        return Response(location_serializer.data, status=status.HTTP_200_OK)


class AdminLocationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = StationLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)
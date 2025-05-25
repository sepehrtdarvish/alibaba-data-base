from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator


from ticket.models import StationLocation, LocationType
from ticket.serializers import GetLocationSerializer, StationLocationModelSerializer, TicketWriteSerializer, TicketModelSerializer
from ticket.decorators import company_required

from django.conf import settings

class LocationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = GetLocationSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        location_type = serializer.validated_data['type']
        locations = StationLocation.objects.filter(location_type=location_type)

        location_serializer = StationLocationModelSerializer(locations, many=True)

        return Response(location_serializer.data, status=status.HTTP_200_OK)


class CompanyOwnerTicketView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(company_required)
    def post(self, request):
        company = request.company
        
        serializer = TicketWriteSerializer(data=request.data, context={'company': company})
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()

        ticket_serializer = TicketModelSerializer(ticket)

        return Response(ticket_serializer.data, status=status.HTTP_200_OK)
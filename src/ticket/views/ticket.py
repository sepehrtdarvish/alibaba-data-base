from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator


from ticket.models import StationLocation, LocationType
from ticket.serializers import GetLocationSerializer, StationLocationModelSerializer, TicketWriteSerializer, TicketModelSerializer
from users.decorators import company_required

from django.conf import settings


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
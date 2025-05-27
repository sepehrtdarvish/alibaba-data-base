from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.db.models import Q


from ticket.models import StationLocation, LocationType, Ticket
from ticket.serializers import GetLocationSerializer, TicketQuerySerializer, TicketWriteSerializer, TicketModelSerializer
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

        return Response(TicketModelSerializer(ticket).data, status=status.HTTP_200_OK)
    

class TicketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = Q()

        serializer = TicketQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        origin = serializer.validated_data.get('origin', None)
        if origin:
            query &= Q(origin=origin)

        destination = serializer.validated_data.get('destination', None)
        if destination:
            query &= Q(destination=destination)

        start_at = serializer.validated_data.get('start_at', None)
        if start_at:
            query &= Q(start_at__gte=start_at)

        min_price = serializer.validated_data.get('min_price', None)
        if min_price:
            query &= Q(price__gte=min_price)

        max_price = serializer.validated_data.get('max_price', None)
        if max_price:
            query &= Q(price__lte=max_price)

        class_type = serializer.validated_data.get('class_type', None)
        if class_type:
            query &= Q(class_type=class_type)

        tickets = Ticket.objects.filter(query)

        return Response(TicketModelSerializer(tickets, many=True).data, status=status.HTTP_200_OK)
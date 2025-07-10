from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.db import connection
from company.models import Company
from company.serializers import CompanyReadSerializer
from ticket.models import Ticket
from ticket.serializers import TicketQuerySerializer, TicketWriteSerializer, TicketModelSerializer
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
    
class CompanyView(APIView):
    def get(self, request):
        companies = Company.objects.all()
        
        return Response(CompanyReadSerializer(companies, many=True).data, status=status.HTTP_200_OK)
    

class TicketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        query = Q()

        serializer = TicketQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        """
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
        """
        tickets = self.get_filtered_tickets_sql(serializer.validated_data)

        return Response(TicketModelSerializer(tickets, many=True).data, status=status.HTTP_200_OK)
    
    def get_filtered_tickets_sql(self, params):
        sql = "SELECT * FROM ticket_ticket WHERE 1=1"
        values = []

        origin = params.get('origin').id
        if origin:
            sql += " AND origin_id = %s"
            values.append(origin)
        
        destination = params.get('destination').id
        if destination:
            sql += " AND destination_id = %s"
            values.append(destination)

        delay = params.get('delay')
        print(delay)
        if delay:
            sql += " AND delay = %s"
            values.append(str(delay))

        stops = params.get('stops')
        if stops:
            sql += " AND stops = %s"
            values.append(str(stops))


        start_at = params.get('start_at')
        print(start_at)
        if start_at:
            sql += " AND start_at >= %s"
            values.append(start_at)




        with connection.cursor() as cursor:
            cursor.execute(sql, values)
            ids = [row[0] for row in cursor.fetchall()]

        return Ticket.objects.filter(id__in=ids).prefetch_related('sections__section__vehicle')
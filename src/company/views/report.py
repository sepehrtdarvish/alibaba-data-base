from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.decorators import method_decorator
from users.decorators import company_required
from django.db import connection
from company.models import Report
from company.serializers import ReportWriteSerializer, ReportModelSerializer, ReportResponseSerializer

class ReportView(APIView):

    def post(self, request):
        serializer = ReportWriteSerializer(data=request.data, context={"user": request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM company_report
                WHERE submitted_by_id = %s
                ORDER BY created_at DESC;
            """, [request.user.id])
            report_ids = [row[0] for row in cursor.fetchall()]

        reports = Report.objects.filter(id__in=report_ids)
        serializer = ReportModelSerializer(reports, many=True)
        return Response(serializer.data)

class ReportCompanyView(APIView):

    def post(self, request):
        serializer = ReportResponseSerializer(data=request.data, context=request.user)
        serializer.is_valid(raise_exception=True)
        
        return Response




    def get(self, request):
        reports = Report.objects.all()
        serializer = ReportModelSerializer(reports, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    
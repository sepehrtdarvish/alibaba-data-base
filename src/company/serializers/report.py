from rest_framework import serializers
from ticket.models import Reservation, Ticket
from company.models import ReportType, Report
from django.utils import timezone

from django.db import transaction, connection
import uuid


class ReportWriteSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=1000)
    subject = serializers.ChoiceField(choices=ReportType.choices)
    reservation = serializers.PrimaryKeyRelatedField(
        queryset = Reservation.objects.all(), required=False
    )
    ticket = serializers.PrimaryKeyRelatedField(
        queryset = Ticket.objects.all(), required=False
    )

    def validate(self, attrs):
        subject = attrs['subject']

        if subject == ReportType.RESERVATION:
            if not attrs.get('reservation', None):
                raise serializers.ValidationError('Reservation Type needs Reservation ID.')
        else:
            if attrs.get('reservation', None):
                raise serializers.ValidationError('Only Reservation Type Can have Reservation ID.')
            
        if subject == ReportType.TICKET:
            if not attrs.get('ticket', None):
                raise serializers.ValidationError('Ticket Type needs Ticket ID.')
        else:
            if attrs.get('reservation', None):
                raise serializers.ValidationError('Only Ticket Type Can have Ticket ID.')
            
        return attrs
    
    def create(self, validated_data):
        submitted_by_id = self.context['user'].id
        ticket = validated_data.get('ticket')
        reservation = validated_data.get('reservation')

        ticket_id = ticket.id if ticket else None
        reservation_id = reservation.id if reservation else None

        report_uuid = uuid.uuid4()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO company_report (id, subject, description, submitted_by_id, ticket_id, reservation_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, Now())
                RETURNING *;
            """, [
                report_uuid,
                validated_data['subject'],
                validated_data['description'],
                submitted_by_id,
                ticket_id,
                reservation_id
            ])
            columns = [col[0] for col in cursor.description]
            report_row = cursor.fetchone()

        return dict(zip(columns, report_row))

class ReportModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'



class ReportResponseSerializer(serializers.Serializer):
    report = serializers.PrimaryKeyRelatedField(
        queryset = Report.objects.all(),
        required = True
    )
    response = serializers.CharField(max_length=100)

    def create(self, validated_data):
        report = validated_data['report']
        response = validated_data.get('response')
        updated_at = timezone.now()
        inspected_by_id = self.context['user'].id
        proccessed_at = timezone.now()

        # report.response = validated_data.get('response')
        # report.update_at = timezone.now()
        # report.inspected_by = self.context['user']
        # report.proccessed_at = timezone.now()
        # report.save()

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE company_report
                SET response = %s,
                    updated_at = %s,
                    inspected_by_id = %s,
                    proccessed_at = %s
                WHERE id = %s;
            """, [
                response,
                updated_at,
                inspected_by_id,
                proccessed_at,
                report.id
            ])

        updated_report = Report.objects.get(id=report.id)
        return updated_report
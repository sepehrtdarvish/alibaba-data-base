from rest_framework import serializers
from ticket.models import Reservation, Ticket
from company.models import ReportType, Report
from django.utils import timezone

from django.db import transaction

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
        report = Report.objects.create(
            subject = validated_data['subject'],
            description = validated_data['description'],
            submitted_by = self.context['user'],
            ticket = validated_data.get('ticket', None),
            reservation = validated_data.get('reservation', None)
        )

        return report
    

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
        report.response = validated_data.get('response')
        report.update_at = timezone.now()
        report.inspected_by = self.context['user']
        report.proccessed_at = timezone.now()

        report.save()

        return report
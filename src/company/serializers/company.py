from rest_framework import serializers
from ticket.models import StationLocation
from company.models import ReportType, RefundRule

from django.db import transaction


class RefundRuleWriteSerializer(serializers.Serializer):
    days = serializers.IntegerField()
    percentage = serializers.IntegerField()


    def validate_days(self, obj):
        if obj > 120 or obj < 1:
            raise serializers.ValidationError('Invalid days field')
        
        return obj
        
    def validate_percentage(self, obj):
        if obj < 0 or obj > 100:
            raise serializers.ValidationError('Invalid percentage field')

        return obj

class CompanyPolicyWriteSerializer(serializers.Serializer):
    rules = RefundRuleWriteSerializer(many=True, required=True)

    def validate_rules(self, obj):
        if len(obj) < 1:
            raise serializers.ValidationError('You need to add at least one refund rule')
        
        return obj


    def create(self, validated_data):
        company = self.context['company']
        created_rules = []

        with transaction.atomic():
            for rule in validated_data['rules']:
                refund_rule = RefundRule.objects.create(
                    **rule,
                    company=company
                    )
                
                created_rules.append(refund_rule)
        
        return created_rules
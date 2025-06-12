from rest_framework import serializers
from ticket.models import StationLocation
from company.models import Company

from django.db import transaction, connection
import uuid

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
                columns = []
                values = []
                placeholders = []

                for key, value in rule.items():
                    columns.append(key)
                    values.append(value)
                    placeholders.append('%s')

                new_id = str(uuid.uuid4())
                columns.append('id')
                values.append(new_id)
                placeholders.append('%s')

                columns.append('company_id')
                values.append(company.id)
                placeholders.append('%s')

                sql = f"""
                    INSERT INTO company_refundrule ({', '.join(columns)})
                    VALUES ({', '.join(placeholders)})
                    RETURNING *;
                """

                with connection.cursor() as cursor:
                    cursor.execute(sql, values)
                    cols = [col[0] for col in cursor.description]
                    row = cursor.fetchone()
                    refund_rule = dict(zip(cols, row))

                created_rules.append(refund_rule)
                
        return created_rules


class CompanyReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
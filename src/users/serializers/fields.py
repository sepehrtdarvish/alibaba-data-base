import phonenumbers
from rest_framework import serializers


class PhoneNumberField(serializers.CharField):

    def to_internal_value(self, data):
        try:
            # Parse the phone number with the 'IR' region
            parsed_number = phonenumbers.parse(data, 'IR')
            # Check if it's a valid number
            if phonenumbers.is_valid_number(parsed_number):
                # Optionally format the number to E164 (standard international format)
                return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            raise serializers.ValidationError('شماره تلفن معتبر نیست')
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError('فرمت شماره تلفن اشتباه است.')

from rest_framework import serializers
from users.models import Profile


class ProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100, required=False)
    home_town = serializers.CharField(max_length=40, require=False)
    birthdate = serializers.DateField(require=False)

    def create(self, validated_data):
        user = self.context['user']
        Profile.objects.create(
            user = user,
            full_name = validated_data.get('full_name', None),
            home_town = validated_data.get('home_town', None),
            birthdate = validated_data.get('birthdate', None),
        )

    def update(self, validated_data):
        user = self.context['user']
        profile = user.profile

        full_name = validated_data.get('full_name', None)
        home_town = validated_data.get('home_town', None)
        birthdate = validated_data.get('birthdate', None)

        profile.full_name = full_name if full_name else profile.full_name
        profile.home_town = home_town if home_town else profile.home_town
        profile.birthdate = birthdate if birthdate else profile.birthdate

        profile.save()
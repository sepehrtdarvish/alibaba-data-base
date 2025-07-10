from rest_framework import serializers
from users.models import Profile


class ProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100, required=True)
    home_town = serializers.CharField(max_length=40, required=True)
    birthdate = serializers.DateField(required=True)


    def validate(self, attrs):
        user = self.context['user']
        if Profile.objects.filter(user=user):
            raise serializers.ValidationError('user already has a profile')


    def create(self, validated_data):
        user = self.context['user']
        Profile.objects.create(
            user = user,
            full_name = validated_data.get('full_name', None),
            home_town = validated_data.get('home_town', None),
            birthdate = validated_data.get('birthdate', None),
        )

class ProfileUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100, required=True)
    home_town = serializers.CharField(max_length=40, required=True)
    birthdate = serializers.DateField(required=True)

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
        
    

class ProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
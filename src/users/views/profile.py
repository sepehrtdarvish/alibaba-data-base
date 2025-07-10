import json
from users.serializers import ProfileSerializer, ProfileUpdateSerializer, ProfileModelSerializer
from django.db import connection
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        cache_key = f"user:profile:{user_id}"

        cached_profile = cache.get(cache_key)
        if cached_profile:
            profile_data = json.loads(cached_profile)
            return Response(profile_data, status=status.HTTP_200_OK)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, full_name, home_town, birthdate
                FROM users_profile
                WHERE user_id = %s
            """, [user_id])
            row = cursor.fetchone()

        if not row:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        profile_data = {
            "id": row[0],
            "user": row[1],
            "full_name": row[2],
            "home_town": row[3],
            "birthdate": str(row[4]) if row[4] else None,
        }

        return Response(profile_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_id = request.user.id
        if user_id:
            cache.delete(f"user:profile:{user_id}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        user_id = request.user.id

        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users_profile WHERE user_id = %s", [user_id])
            row = cursor.fetchone()
            if not row:
                return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
            profile_id = row[0]

        request.data['id'] = profile_id
        serializer = ProfileUpdateSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        serializer.update(validated_data)

        cache.delete(f"user:profile:{user_id}")

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, full_name, home_town, birthdate
                FROM users_profile
                WHERE user_id = %s
            """, [user_id])
            row = cursor.fetchone()

        if not row:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        profile_data = {
            "id": row[0],
            "user": row[1],
            "full_name": row[2],
            "home_town": row[3],
            "birthdate": str(row[4]) if row[4] else None,
        }

        return Response(profile_data, status=status.HTTP_200_OK)


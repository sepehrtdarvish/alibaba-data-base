from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.decorators import method_decorator
from users.decorators import company_required

from company.serializers import CompanyPolicyWriteSerializer



class CompanyPolicyView(APIView):
    
    @method_decorator(company_required)
    def post(self, request):
        company = request.company
        serializer = CompanyPolicyWriteSerializer(data=request.data, context={'company': company})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)
    
from rest_framework.exceptions import APIException


class CompanyNotFoundException(APIException):
    status_code = 404
    default_detail = 'Company Not Found.'
    default_code = 'company_not_found'
from rest_framework.exceptions import APIException


class UserNotFoundException(APIException):
    status_code = 404
    default_detail = 'User Not Found.'
    default_code = 'user_not_found'

class AuthenticationFailed(APIException):
    status_code = 404
    default_detail = 'Invalid Password or Code'
    default_code = 'authentication_failed'
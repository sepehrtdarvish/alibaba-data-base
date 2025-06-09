import re
from users.models import UserAccount
from users.exceptions import UserNotFoundException

def detect_identifier_type(identifier):
    if re.match(r"^\+?\d{10,15}$", identifier):
        return 'phone_number'
    elif '@' in identifier:
        return 'email'
    else:
        return 'username'
    

def get_user_or_404(identifier, type):
    if type == 'email':
        user = UserAccount.objects.filter(email=identifier).first()
    elif type == 'username':
        user = UserAccount.objects.filter(username=identifier).first()
    else:
        user = UserAccount.objects.filter(phone_number=identifier).first()

    if not user:
        raise UserNotFoundException
    
    return user
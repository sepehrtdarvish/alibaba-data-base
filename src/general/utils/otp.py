import uuid

from django.core.cache import cache


def generate_otp(email):
    # TODO: otp = random.randint(100000, 999999)
    otp = '1234'
    cache.set(f'otp_{email}', otp, timeout=300)  # Store OTP for 5 minutes
    return otp


def verify_otp(email, otp):
    cached_otp = cache.get(f'otp_{email}')
    
    if str(cached_otp) == str(otp):
        cache.delete(f'otp_{email}')
        return True
    return False


def generate_user_token(email):
    token = uuid.uuid4().hex
    cache.set(f'token_{token}', email, timeout=3000)  # Store token for 50 minutes
    return token


def get_user_by_token(token):
    cached_email = cache.get(f'token_{token}')
    if cached_email:
        return cached_email
    return None

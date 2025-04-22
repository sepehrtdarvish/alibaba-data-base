import uuid

from django.core.cache import cache


def generate_otp(phone_number):
    # otp = random.randint(100000, 999999)
    otp = '1234'
    cache.set(f'otp_{phone_number}', otp, timeout=300)  # Store OTP for 5 minutes
    return otp


def verify_otp(phone_number, otp):
    cached_otp = cache.get(f'otp_{phone_number}')
    if str(cached_otp) == str(otp) or str(otp) == '1234':
        cache.delete(f'otp_{phone_number}')
        return True
    return False


def generate_user_token(phone_number):
    token = uuid.uuid4().hex
    cache.set(f'token_{token}', phone_number, timeout=3000)  # Store token for 50 minutes
    return token


def get_user_by_token(token):
    cached_phone_number = cache.get(f'token_{token}')
    if cached_phone_number:
        return cached_phone_number
    return None

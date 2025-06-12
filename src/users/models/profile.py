from django.db import models
import uuid
from users.models import UserAccount


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    home_town = models.CharField(max_length=30)
    birthdate = models.DateField()
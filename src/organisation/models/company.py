from django.db import models
import uuid

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
from django.db import models
import uuid

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='/logos', null=True)
    owner = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)
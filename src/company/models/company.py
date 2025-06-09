from django.db import models
import uuid

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='company_logo_images/')
    owner = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)


class RefundRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name='rules', on_delete=models.CASCADE)
    days = models.PositiveIntegerField()
    percentage = models.PositiveIntegerField()

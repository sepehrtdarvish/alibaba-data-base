from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
import uuid


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    balance = models.FloatField()
    user = models.OneToOneField("users.UserAccount", on_delete=models.CASCADE, related_name='wallet')
    updated_at = models.DateTimeField(auto_now=True)


class TransactionType(models.TextChoices):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    REFUND = "REFUND"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=TransactionType.choices)
    amount = models.FloatField()
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

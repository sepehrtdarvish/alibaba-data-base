from django.db import models
import uuid

class VehicleTypes(models.TextChoices):
    Train = 'Train'
    AirPlane = 'AirPlane'
    Bus = 'Bus'


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=VehicleTypes.choices)
    capacity = models.PositiveIntegerField()
    company = models.ForeignKey('company.Company', on_delete=models.PROTECT, null=True)
    unicode = models.CharField(max_length=20, null=True)
    catering_service = models.BooleanField(default=False)
    wifi_access = models.BooleanField(default=False)
    television = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)



class SectionType(models.TextChoices):
    economy = 'economy'
    vip = 'vip'
    business = 'business'


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=SectionType.choices)
    start_number = models.PositiveIntegerField()
    end_number = models.PositiveIntegerField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='sections')
    tickets = models.ManyToManyField('ticket.Ticket', through='ticket.TicketSection')

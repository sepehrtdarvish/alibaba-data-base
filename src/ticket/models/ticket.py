from django.db import models
import uuid
from organisation.models import Vehicle


class TicketType(models.TextChoices):
    economy = 'economy'
    vip = 'vip'
    business = 'business'


class LocationType(models.TextChoices):
    airport = 'airport'
    terminal = 'terminal'
    train_station = 'train_station'


class StationLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    location_type = models.CharField(max_length=20, choices=LocationType.choices)


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    origin = models.ForeignKey(StationLocation, related_name='origin_tickets', on_delete=models.CASCADE)
    destination = models.ForeignKey(StationLocation, related_name='destination_tickets', on_delete=models.CASCADE)
    price = models.FloatField()
    start_at = models.DateTimeField()
    duration = models.DurationField()
    delay = models.DurationField(null=True, blank=True)
    class_type = models.CharField(max_length=20, choices=TicketType.choices)
    capacity = models.PositiveIntegerField()
    vehicle_type = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    stops = models.PositiveIntegerField(null=True, blank=True)


class LocationType(models.TextChoices):
    airport = 'airport'
    terminal = 'terminal'
    train_station = 'train_station'



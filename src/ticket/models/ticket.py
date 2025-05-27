from django.db import models
import uuid
from organisation.models import Vehicle


class LocationType(models.TextChoices):
    airport = 'airport'
    terminal = 'terminal'
    train_station = 'train_station'


class StationLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    type = models.CharField(max_length=20, choices=LocationType.choices)


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    origin = models.ForeignKey(StationLocation, related_name='origin_tickets', on_delete=models.CASCADE)
    destination = models.ForeignKey(StationLocation, related_name='destination_tickets', on_delete=models.CASCADE)
    price = models.FloatField()
    start_at = models.DateTimeField()
    duration = models.DurationField()
    delay = models.DurationField(null=True, blank=True)
    capacity = models.PositiveIntegerField()
    stops = models.PositiveIntegerField(null=True, blank=True)


class TicketSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey('organisation.Section', on_delete=models.CASCADE, null=True)
    price = models.FloatField()
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, related_name='sections')


class LocationType(models.TextChoices):
    airport = 'airport'
    terminal = 'terminal'
    train_station = 'train_station'



from django.db import models
import uuid

class VehicleTypes(models.TextChoices):
    Train = 'Train'
    AirPlane = 'AirPlane'
    Bus = 'Bus'

class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField()
    vehicle_info = models.CharField(max_length=20, choices=VehicleTypes.choices)

class TrainServices(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flatbed_wagon = models.BooleanField(default=False)
    catering_services = models.BooleanField(default=False)
    wifi_access = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)

class Train(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    train_services = models.OneToOneField(TrainServices, on_delete=models.CASCADE)
    star_number = models.IntegerField(choices=[(i, i) for i in range(3, 6)])
    private_compartment = models.CharField(max_length=50)
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE)

class AirplaneServices(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catering_services = models.BooleanField(default=False)
    wifi_access = models.BooleanField(default=False)
    bendable_seats = models.BooleanField(default=False)


class AirPlaneClassTypes(models.TextChoices):
    Economy = 'Economy'
    Business = 'Business'
    FirstClass = 'FirstClass'


class AirPlane(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    airplane_services = models.OneToOneField(AirplaneServices, on_delete=models.CASCADE)
    flight_number = models.CharField(max_length=50, unique=True)
    flight_class = models.CharField(max_length=20, choices=AirPlaneClassTypes.choices)


class BusServices(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catering_services = models.BooleanField(default=False)
    individual_screen = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)


class BusClassTypes(models.TextChoices):
    VIP = 'VIP'
    Normal = 'Normal'
    Sleepable = 'Sleepable'

class BusSeatTypes(models.TextChoices):
    ONEONE = '1+1'
    TWOONE = '2+1'


class Bus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bus_services = models.OneToOneField(BusServices, on_delete=models.CASCADE)
    bus_type = models.CharField(max_length=20, choices=BusClassTypes.choices)
    seat_kind = models.CharField(max_length=10, choices=BusSeatTypes.choices)

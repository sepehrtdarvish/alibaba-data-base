from django.db import models
import uuid


class VehicleTypes(models.TextChoices):
    Train = 'Train'
    AirPlane = 'AirPlane'
    Bus = 'Bus'


class Services(models.Model):
    catering_service = models.BooleanField()
    wifi_access = models.BooleanField()


class TrainServices(Services):
    flatbed_wagon = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)
    television = models.BooleanField(default=False)


class AirplaneServices(Services):
    bendable_seats = models.BooleanField(default=False)


class BusServices(Services):
    individual_screen = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capacity = models.PositiveIntegerField()
    services = models.ForeignKey(Services, on_delete=models.CASCADE)
    company = models.ForeignKey('organisation.Company', on_delete=models.PROTECT, null=True)


class Train(Vehicle):
    star_number = models.IntegerField(choices=[(i, i) for i in range(3, 6)])
    unicode = models.CharField(max_length=50)


class AirPlaneClassTypes(models.TextChoices):
    Economy = 'Economy'
    Business = 'Business'
    FirstClass = 'FirstClass'


class AirPlaneClasses(models.TextChoices):
    Airbus = "Airbus"
    Privet_Jet = "PrivetJet"


class AirPlane(Vehicle):
    unicode = models.CharField(max_length=50, unique=True)
    flight_class = models.CharField(max_length=20, choices=AirPlaneClasses.choices)


class BusClassTypes(models.TextChoices):
    VIP = 'VIP'
    Normal = 'Normal'
    Sleepable = 'Sleepable'


class BusSeatTypes(models.TextChoices):
    ONEONE = '1+1'
    TWOONE = '2+1'


class Bus(Vehicle):
    bus_type = models.CharField(max_length=20, choices=BusClassTypes.choices)
    seat_kind = models.CharField(max_length=10, choices=BusSeatTypes.choices)
    license_plate = models.CharField(max_length=15)


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    start_number = models.PositiveIntegerField()
    end_number = models.PositiveIntegerField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='sections')
    tickets = models.ManyToManyField('ticket.Ticket', through='ticket.TicketSection')
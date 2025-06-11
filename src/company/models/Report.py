from django.db import models
import uuid


class ReportType(models.TextChoices):
    PAYMENT = 'payment'
    DELAY = 'delay'
    TICKET = 'ticket'
    RESERVATION = 'reservation'
    OTHER = 'other'

class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    subject = models.CharField(max_length=20, choices=ReportType.choices)
    reservation = models.ForeignKey('ticket.Reservation', on_delete=models.CASCADE, related_name='reports', null=True)
    response = models.TextField(null=True)
    ticket = models.ForeignKey('ticket.Ticket', on_delete=models.CASCADE, related_name='reports', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    submitted_by = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE, related_name='submitted_reports')
    inspected_by = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE, null=True, blank=True, related_name='inspected_reports')
    proccessed_at = models.DateTimeField(null=True, blank=True)
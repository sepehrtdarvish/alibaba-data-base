from django.db import models
import uuid


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)
    ticket_section = models.ForeignKey('ticket.TicketSection', on_delete=models.CASCADE, null=True)
    seat_number = models.PositiveIntegerField()
    transaction = models.ForeignKey('ticket.Transaction', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_cancelled = models.BooleanField(default=False)

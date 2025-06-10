from django.utils import timezone
from django.core.cache import cache


def get_refund_amount(reservation):
        company = reservation.ticket_section.section.vehicle.company
        ticket_start_date = reservation.ticket_section.ticket.start_at
        today_date = timezone.now()
        remain_days = (ticket_start_date - today_date).days
        refund_rule = company.rules.filter(days__lte=remain_days).order_by('-days').first()

        if not refund_rule:
            refund_percentage = 0
        else:
            refund_percentage = refund_rule.refund_percentage

        refund_amount = reservation.ticket_section.price * refund_percentage / 100


        return refund_amount


def reserve_ticket(user_id, ticket_seat_id, seat_number, payment_token):
    cache.set(
        f'reservation_{user_id}',
            {
                "ticket_seat_id": ticket_seat_id,
                "seat_number": seat_number,
                "payment_token": payment_token
            },
            timeout=600
        ) # Store for 10 minutes
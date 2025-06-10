from django.utils import timezone
from django.core.cache import cache
import time


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


def reserve_ticket(payment_token, user_id, ticket_section_id, seat_number):
    seat_lock_key = f"seat_lock_{ticket_section_id}_{seat_number}"

    cache.set(seat_lock_key, user_id, timeout=600)

    cache.set(
        f"r_token_{payment_token}",
        {
            'user_id': user_id,
            'ticket_section_id': ticket_section_id,
            'seat_number': seat_number,
            'payment_token': payment_token,
            'reserved_at': int(time.time())
        },
        timeout=600
    )

    reserved_map_key = f"reserved_seats_map_{ticket_section_id}"
    reserved_map = cache.get(reserved_map_key) or {}

    expires_at = int(time.time()) + 600
    reserved_map[seat_number] = expires_at

    cache.set(reserved_map_key, reserved_map, timeout=600)

    

def get_reserved_seats(ticket_section_id):
    reserved_map_key = f"reserved_seats_map_{ticket_section_id}"
    reserved_map = cache.get(reserved_map_key) or {}

    now = int(time.time())
    new_reserved_map = {}
    still_reserved = []

    for seat, expires_at in reserved_map.items():
        if expires_at > now:
            still_reserved.append(seat)
            new_reserved_map[seat] = expires_at

    cache.set(reserved_map_key, new_reserved_map, timeout=600)

    return still_reserved

def find_seat_number(capacity, reserved_seats):
    for i in range(1, capacity + 1):
        if i not in reserved_seats:
            return i
    return None
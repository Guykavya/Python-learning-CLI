from datetime import datetime, timezone
from decimal import Decimal


def parse_utc(text, field):
    """ISO 8601 text with an offset -> aware datetime in UTC. No offset -> ValueError."""
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None:
        raise ValueError(f"{field}: timestamp {text!r} has no timezone offset")
    return moment.astimezone(timezone.utc)


def flatten_order(order):
    """Return a new flat dict with typed, normalised values (see problem.md)."""
    customer = order["customer"]
    city = customer["city"]
    if city is not None:
        city = city.strip().title() or None       # blank -> None
    items = order["items"]
    return {
        "id": order["id"],
        "email": customer["email"].strip().lower(),
        "city": city,
        "status": order["status"].strip().lower(),
        "amount": Decimal(order["amount"].strip()),
        "currency": order["currency"].strip().upper(),
        "created_at": parse_utc(order["created_at"], "created_at"),
        "updated_at": parse_utc(order["updated_at"], "updated_at"),
        "item_count": len(items),
        "total_qty": sum(item["qty"] for item in items),
    }

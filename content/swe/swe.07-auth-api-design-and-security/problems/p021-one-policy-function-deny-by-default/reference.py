from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    role: str


@dataclass(frozen=True)
class Order:
    id: int
    owner_id: int
    status: str
    total_cents: int


REFUND_LIMIT_FOR_SUPPORT = 10_000


def can(user, action, order=None, *, amount=0):
    if user is None:
        return False
    if user.role == "admin":
        return action in {"read", "cancel", "refund", "list_all"}
    if user.role == "support":
        if action in {"read", "list_all"}:
            return True
        if action == "refund":
            return order is not None and amount <= REFUND_LIMIT_FOR_SUPPORT
        return False
    if user.role == "customer":
        if order is None:
            return False
        owns = order.owner_id == user.id
        if action == "read":
            return owns
        if action == "cancel":
            return owns and order.status == "pending"
        return False
    return False

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    role: str                      # "customer" | "support" | "admin"


@dataclass(frozen=True)
class Order:
    id: int
    owner_id: int
    status: str                    # "pending" | "paid" | "cancelled"
    total_cents: int


REFUND_LIMIT_FOR_SUPPORT = 10_000          # 100.00 in cents


def can(user, action, order=None, *, amount=0):
    return True                    # TODO: replace this with the rules of the statement

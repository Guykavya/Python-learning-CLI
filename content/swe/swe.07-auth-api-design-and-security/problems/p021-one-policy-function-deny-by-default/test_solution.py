import pytest

from solution import Order, User, can

ada, bo = User(1, "customer"), User(2, "customer")
sam, root = User(3, "support"), User(4, "admin")
intern = User(5, "intern")
pending = Order(10, owner_id=1, status="pending", total_cents=2500)
paid = Order(11, owner_id=1, status="paid", total_cents=2500)
bos_pending = Order(12, owner_id=2, status="pending", total_cents=900)

# (label, user, action, order, amount, expected)
CASES = [
    ("owner reads own pending order", ada, "read", pending, 0, True),
    ("owner reads own paid order", ada, "read", paid, 0, True),
    ("other customer reads it", bo, "read", pending, 0, False),
    ("owner cancels own pending order", ada, "cancel", pending, 0, True),
    ("owner cancels own paid order", ada, "cancel", paid, 0, False),
    ("other customer cancels it", bo, "cancel", pending, 0, False),
    ("customer refunds own order", ada, "refund", paid, 0, False),
    ("customer lists all orders", ada, "list_all", None, 0, False),
    ("customer reads with no order", ada, "read", None, 0, False),
    ("support reads any order", sam, "read", bos_pending, 0, True),
    ("support lists all orders", sam, "list_all", None, 0, True),
    ("support cancels", sam, "cancel", pending, 0, False),
    ("support refunds 50.00", sam, "refund", paid, 5_000, True),
    ("support refunds exactly 100.00", sam, "refund", paid, 10_000, True),
    ("support refunds 100.01", sam, "refund", paid, 10_001, False),
    ("support refund without an order", sam, "refund", None, 100, False),
    ("admin reads any order", root, "read", bos_pending, 0, True),
    ("admin lists all orders", root, "list_all", None, 0, True),
    ("admin refunds 5000.00", root, "refund", paid, 500_000, True),
    ("admin cancels", root, "cancel", paid, 0, True),
    ("anonymous reads", None, "read", pending, 0, False),
    ("anonymous lists", None, "list_all", None, 0, False),
    ("unknown action by admin", root, "format_disk", pending, 0, False),
    ("unknown action by customer", ada, "delete", pending, 0, False),
    ("unknown role reads", intern, "read", pending, 0, False),
    ("unknown role lists", intern, "list_all", None, 0, False),
]


@pytest.mark.parametrize("label,user,action,order,amount,expected", CASES, ids=[c[0] for c in CASES])
def test_policy_table(label, user, action, order, amount, expected):
    got = can(user, action, order, amount=amount)
    assert got is expected, (
        f"{label}: can(...) returned {got!r}, expected {expected}. "
        + ("A rule is missing: this must be allowed." if expected else
           "Deny by default: allow only what a rule names, and end the function with return False."))


def test_always_returns_a_real_bool():
    for _, user, action, order, amount, _ in CASES:
        assert type(can(user, action, order, amount=amount)) is bool, "Return True or False, not None or a truthy object."


def test_misspelt_actions_are_denied_for_every_role():
    for user in (ada, sam, root, intern, None):
        for action in ("Read", "READ", "reed", "", "read ", "refunds", "cancel_all"):
            assert can(user, action, pending) is False, f"Action {action!r} is not in the list, so {user} must be denied. Compare action names exactly."


def test_ownership_uses_the_ids_not_the_roles():
    other = User(1, "customer")                       # same id as Ada: same person
    assert can(other, "read", pending) is True
    assert can(User(99, "customer"), "read", pending) is False

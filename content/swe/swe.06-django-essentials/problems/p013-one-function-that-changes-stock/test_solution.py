import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection
from django.test.utils import CaptureQueriesContext

from solution import Item, Movement, move_stock


@pytest.fixture
def pen():
    return Item.objects.create(name="pen", quantity=10)


def test_receive_adds_stock_and_records_a_movement(pen):
    m = move_stock(pen, 5, "receive")
    assert pen.quantity == 15, f"After +5 the instance should show 15 (refresh it), got {pen.quantity}."
    assert Item.objects.get(pk=pen.pk).quantity == 15, "The database row must hold 15."
    assert isinstance(m, Movement), f"move_stock must return the new Movement, got {m!r}."
    assert (m.item_id, m.delta, m.reason, m.user_id) == (pen.pk, 5, "receive", None), (
        f"The Movement must hold item, delta, reason and user, got {(m.item_id, m.delta, m.reason, m.user_id)}.")
    assert Movement.objects.count() == 1, "Exactly one Movement per call."


def test_sale_removes_stock_and_stores_the_user(pen):
    user = get_user_model().objects.create_user("asha", password="x")
    m = move_stock(pen, -4, "sale", user=user)
    assert pen.quantity == 6 and Item.objects.get(pk=pen.pk).quantity == 6, "10 - 4 must leave 6."
    assert Movement.objects.get(pk=m.pk).user_id == user.pk, "The Movement must store the user who did it."


def test_removing_exactly_everything_is_allowed(pen):
    move_stock(pen, -10, "sale")
    assert Item.objects.get(pk=pen.pk).quantity == 0, "Going to exactly 0 is allowed: the rule is quantity >= 0."


def test_oversell_raises_integrity_error_and_changes_nothing(pen):
    with pytest.raises(IntegrityError):
        move_stock(pen, -11, "sale")
    assert Item.objects.get(pk=pen.pk).quantity == 10, "A refused sale must leave the stock at 10."
    assert Movement.objects.count() == 0, (
        "A refused sale must leave NO Movement row. Put both writes inside transaction.atomic() so they roll back together.")


def test_the_constraint_lives_in_the_database(pen):
    names = [c.name for c in Item._meta.constraints]
    assert "item_quantity_not_negative" in names, (
        f"Item.Meta.constraints must hold a CheckConstraint named item_quantity_not_negative, got {names}.")
    with pytest.raises(IntegrityError):
        Item.objects.filter(pk=pen.pk).update(quantity=-1)   # even a direct update is refused


def test_zero_delta_is_a_value_error(pen):
    with pytest.raises(ValueError):
        move_stock(pen, 0, "adjust")
    assert Movement.objects.count() == 0, "A refused call must write nothing."


def test_two_stale_copies_do_not_overwrite_each_other(pen):
    a = Item.objects.get(pk=pen.pk)
    b = Item.objects.get(pk=pen.pk)          # both think quantity == 10
    move_stock(a, 5, "receive")
    move_stock(b, -3, "sale")
    assert Item.objects.get(pk=pen.pk).quantity == 12, (
        "10 + 5 - 3 must be 12. With item.quantity += delta; item.save() the second call writes 7. "
        "Use update(quantity=F('quantity') + delta) so the database does the arithmetic.")
    assert b.quantity == 12, "After the call the instance should be refreshed from the database (refresh_from_db)."


def test_a_few_queries_only(pen):
    with CaptureQueriesContext(connection) as ctx:
        move_stock(pen, 1, "receive")
    assert len(ctx) <= 6, f"move_stock should need only a handful of queries, it used {len(ctx)}."


def test_a_failure_after_the_stock_change_rolls_it_back(pen, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("disk full")
    monkeypatch.setattr(Movement.objects, "create", boom, raising=False)
    try:
        move_stock(pen, 5, "receive")
    except RuntimeError:
        pass
    assert Item.objects.get(pk=pen.pk).quantity == 10, (
        "If recording the Movement fails, the stock change must be undone too (transaction.atomic()).")

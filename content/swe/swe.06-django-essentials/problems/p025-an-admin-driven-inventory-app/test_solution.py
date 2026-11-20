import pytest
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from solution import Category, InsufficientStock, Item, Movement, move_stock


# ---------------------------------------------------------------------------------- helpers

@pytest.fixture
def category():
    return Category.objects.create(name="Cables")


@pytest.fixture
def item(category):
    return Item.objects.create(name="Zebra cable", sku="ZC-1", category=category, price="2.50", quantity=10)


@pytest.fixture
def superuser():
    return User.objects.create_superuser("root", "root@example.com", "pw-root-12345")


@pytest.fixture
def staff():
    return User.objects.create_user("sam", password="pw-sam-12345", is_staff=True)


def give_permission(user, codename, model):
    """The tests build tables by hand, so the permission rows do not exist yet: create the one we need."""
    content_type = ContentType.objects.get_for_model(model)
    permission, _ = Permission.objects.get_or_create(
        codename=codename, content_type=content_type, defaults={"name": codename})
    user.user_permissions.add(permission)


def logged_in(user):
    client = Client()
    client.force_login(user)
    return client


def api_as(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


# ---------------------------------------------------------------------------------- models

def test_models_have_the_fields():
    names = {f.name for f in Item._meta.get_fields()}
    for needed in ("name", "sku", "category", "price", "quantity"):
        assert needed in names, f"Item needs a field called {needed!r}; it has {sorted(names)}."
    assert Item._meta.get_field("sku").unique, "Item.sku must be unique=True."
    names = {f.name for f in Movement._meta.get_fields()}
    for needed in ("item", "delta", "reason", "note", "created_by", "created"):
        assert needed in names, f"Movement needs a field called {needed!r}; it has {sorted(names)}."
    assert str(Category(name="Cables")) == "Cables", "Category.__str__ must return the name."


def test_the_database_itself_refuses_negative_stock(item):
    assert Item._meta.constraints, "Item needs a CheckConstraint(condition=Q(quantity__gte=0), name=...) in Meta.constraints."
    with pytest.raises(IntegrityError):
        from django.db import transaction
        with transaction.atomic():
            Item.objects.filter(pk=item.pk).update(quantity=-1)
    item.refresh_from_db()
    assert item.quantity == 10, "The row must be unchanged after the refused update."


# ---------------------------------------------------------------------------------- move_stock

def test_receive_and_sale_change_stock_and_write_movements(item):
    user = User.objects.create_user("worker", password="pw-worker-12345")
    m1 = move_stock(item, 5, Movement.Reason.RECEIVE, user=user, note="delivery")
    assert item.quantity == 15, f"The item object must show the new quantity 15 (refresh it), got {item.quantity}."
    m2 = move_stock(item, -3, Movement.Reason.SALE)
    assert item.quantity == 12, f"After -3 the quantity must be 12, got {item.quantity}."
    assert Item.objects.get(pk=item.pk).quantity == 12, "The database row must also be 12."
    assert isinstance(m1, Movement) and m1.pk, "move_stock must return the Movement it created."
    assert (m1.delta, m1.reason, m1.note, m1.created_by) == (5, "receive", "delivery", user), (
        f"The movement must store delta, reason, note and user, got {(m1.delta, m1.reason, m1.note, m1.created_by)!r}.")
    assert m2.created_by is None and m2.delta == -3, "Without a user, created_by is None."
    assert Movement.objects.filter(item=item).count() == 2, "Each change needs exactly one Movement row."


def test_selling_everything_is_allowed_but_not_more(item):
    move_stock(item, -10, Movement.Reason.SALE)
    assert item.quantity == 0, "Selling all 10 units is allowed and leaves 0."
    with pytest.raises(InsufficientStock):
        move_stock(item, -1, Movement.Reason.SALE)


def test_overselling_changes_nothing(item):
    with pytest.raises(InsufficientStock):
        move_stock(item, -11, Movement.Reason.SALE)
    assert Item.objects.get(pk=item.pk).quantity == 10, "A refused sale must leave the quantity at 10."
    assert item.quantity == 10, "The item object must show the real quantity (10) after the refusal."
    assert Movement.objects.count() == 0, "A refused sale must not leave a Movement row."


def test_zero_is_meaningless(item):
    with pytest.raises(ValueError):
        move_stock(item, 0, Movement.Reason.ADJUST)
    assert Movement.objects.count() == 0, "A zero movement must not be recorded."


def test_stale_object_does_not_hide_the_real_stock(item):
    Item.objects.filter(pk=item.pk).update(quantity=3)          # someone else sold 7 meanwhile; our object still says 10
    with pytest.raises(InsufficientStock):
        move_stock(item, -5, Movement.Reason.SALE)
    move_stock(item, 1, Movement.Reason.RECEIVE)
    assert Item.objects.get(pk=item.pk).quantity == 4, (
        "Stock must be changed in the database with F('quantity') + delta, not item.quantity = item.quantity + delta: "
        "the in-memory value (10) was out of date, the real value was 3.")


def test_all_or_nothing(item, monkeypatch):
    def boom(self, *args, **kwargs):
        raise RuntimeError("disk full")
    monkeypatch.setattr(Movement, "save", boom)
    with pytest.raises(RuntimeError):
        move_stock(item, 5, Movement.Reason.RECEIVE)
    monkeypatch.undo()
    assert Item.objects.get(pk=item.pk).quantity == 10, (
        "When writing the Movement fails, the quantity change must be rolled back too: wrap the function in transaction.atomic().")


def test_every_change_has_a_movement_and_they_add_up(category):
    item = Item.objects.create(name="Ledger", sku="LG-1", category=category, price="1.00")   # starts at 0
    calls = [(20, "receive"), (-7, "sale"), (-30, "sale"), (4, "adjust"), (-17, "sale"), (-1, "sale")]
    done = 0
    for delta, reason in calls:
        try:
            move_stock(item, delta, reason)
            done += 1
        except InsufficientStock:
            pass
    item.refresh_from_db()
    deltas = list(Movement.objects.filter(item=item).values_list("delta", flat=True))
    assert len(deltas) == done == 4, f"4 of the 6 calls succeed (the -30 and the last -1 are refused), movements: {deltas}."
    assert sum(deltas) == item.quantity == 0, f"The movements must add up to the stock: sum {sum(deltas)}, stock {item.quantity}."
    assert item.quantity >= 0, "Stock must never be negative."


# ---------------------------------------------------------------------------------- admin

def test_admin_anonymous_is_sent_to_login(item):
    r = Client().get("/admin/shop/item/")
    assert r.status_code == 302 and r["Location"].startswith("/admin/login/"), (
        f"An anonymous visitor must be redirected to the admin login, got {r.status_code}. "
        "Is path('admin/', admin.site.urls) in urlpatterns and is Item registered?")


def test_admin_staff_without_permission_gets_403(item, staff):
    r = logged_in(staff).get("/admin/shop/item/")
    assert r.status_code == 403, f"A staff user with no permissions must get 403 on the changelist, got {r.status_code}."


def test_admin_view_only_staff_cannot_change(item, staff, category):
    give_permission(staff, "view_item", Item)
    client = logged_in(staff)
    assert client.get("/admin/shop/item/").status_code == 200, "A staff user with view_item may see the changelist."
    data = {"name": "Hacked", "sku": "ZC-1", "category": category.pk, "price": "2.50"}
    r = client.post(f"/admin/shop/item/{item.pk}/change/", data)
    assert r.status_code == 403, f"A view-only user must get 403 when posting a change, got {r.status_code}."
    item.refresh_from_db()
    assert item.name == "Zebra cable", "The name must not change for a view-only user."


def test_admin_changelist_search_and_filter(superuser, category):
    other = Category.objects.create(name="Chargers")
    Item.objects.create(name="Zebra cable", sku="ZC-1", category=category, price="2.50")
    Item.objects.create(name="Mango charger", sku="MC-9", category=other, price="9.00")
    client = logged_in(superuser)
    r = client.get("/admin/shop/item/")
    body = r.content.decode()
    assert r.status_code == 200, f"The changelist must answer 200 for a superuser, got {r.status_code}."
    assert "Zebra cable" in body and "Mango charger" in body, "Both items must be listed."
    body = client.get("/admin/shop/item/", {"q": "zebra"}).content.decode()
    assert "Zebra cable" in body and "Mango charger" not in body, "?q=zebra must find the item by name (search_fields = name, sku)."
    body = client.get("/admin/shop/item/", {"q": "MC-9"}).content.decode()
    assert "Mango charger" in body and "Zebra cable" not in body, "?q=MC-9 must find the item by SKU."
    body = client.get("/admin/shop/item/", {"category__id__exact": other.pk}).content.decode()
    assert "Mango charger" in body and "Zebra cable" not in body, "list_filter = ('category',) must filter by category."


def test_admin_quantity_is_read_only(superuser, item, category):
    client = logged_in(superuser)
    r = client.get(f"/admin/shop/item/{item.pk}/change/")
    assert r.status_code == 200, f"The change page must open, got {r.status_code}."
    assert 'name="quantity"' not in r.content.decode(), (
        "quantity must not be an input in the form: readonly_fields = ('quantity',).")
    data = {"name": "Renamed cable", "sku": "ZC-1", "category": category.pk, "price": "2.50", "quantity": "999"}
    r = client.post(f"/admin/shop/item/{item.pk}/change/", data)
    assert r.status_code == 302, f"A valid change must redirect (302), got {r.status_code}."
    item.refresh_from_db()
    assert item.name == "Renamed cable", "The name should have been saved."
    assert item.quantity == 10, f"quantity must stay 10 (changed only through movements), got {item.quantity}."


def test_admin_movements_are_an_audit_trail(superuser, item):
    move_stock(item, 2, Movement.Reason.RECEIVE)
    client = logged_in(superuser)
    r = client.get("/admin/shop/movement/")
    assert r.status_code == 200, f"The movement changelist must work (register Movement, give it a __str__), got {r.status_code}."
    assert client.get("/admin/shop/movement/add/").status_code == 403, (
        "Nobody may add movements by hand in the admin (has_add_permission returns False): they come from move_stock.")
    movement = Movement.objects.get()
    assert client.post(f"/admin/shop/movement/{movement.pk}/delete/", {"post": "yes"}).status_code == 403, (
        "Nobody may delete a movement (has_delete_permission returns False).")
    assert Movement.objects.count() == 1, "The movement must still exist."


# ---------------------------------------------------------------------------------- API

def test_api_anonymous_is_refused(item):
    anon = APIClient()
    assert anon.get("/api/items/").status_code == 403, "An anonymous GET /api/items/ must be 403 (IsAuthenticated)."
    r = anon.post(f"/api/items/{item.pk}/move/", {"delta": -1, "reason": "sale"}, format="json")
    assert r.status_code == 403, f"An anonymous move must be 403, got {r.status_code}."
    item.refresh_from_db()
    assert item.quantity == 10, "Nothing may change for an anonymous request."


def test_api_list_is_cheap_and_complete(category):
    other = Category.objects.create(name="Chargers")
    for i in range(15):
        Item.objects.create(name=f"Item {i:02d}", sku=f"S-{i}", category=category if i % 3 else other, price="1.50", quantity=i)
    user = User.objects.create_user("reader", password="pw-reader-12345")
    client = api_as(user)
    with CaptureQueriesContext(connection) as ctx:
        r = client.get("/api/items/")
    assert r.status_code == 200, f"A logged-in user may list items, got {r.status_code}."
    data = r.json()
    rows = data["results"] if isinstance(data, dict) else data
    assert len(rows) == 15, f"All 15 items must be listed (no pagination is configured), got {len(rows)}."
    assert {"id", "name", "sku", "category", "category_name", "price", "quantity"} <= set(rows[0]), f"Missing fields in {sorted(rows[0])}."
    assert {row["category_name"] for row in rows} == {"Cables", "Chargers"}, "category_name must show the category's name."
    assert len(ctx) <= 2, (
        f"Listing 15 items took {len(ctx)} queries, at most 2 are allowed. "
        "Use Item.objects.select_related('category') in the viewset.")


def test_api_stock_cannot_be_written_directly(item):
    client = api_as(User.objects.create_user("boss", password="pw-boss-12345", is_staff=True))
    r = client.patch(f"/api/items/{item.pk}/", {"quantity": 999}, format="json")
    assert r.status_code in (403, 405), f"There is no way to PATCH an item (stock changes through /move/), got {r.status_code}."
    item.refresh_from_db()
    assert item.quantity == 10, "quantity must not change."


def test_api_move_needs_staff(item):
    user = User.objects.create_user("plain", password="pw-plain-12345")
    r = api_as(user).post(f"/api/items/{item.pk}/move/", {"delta": -1, "reason": "sale"}, format="json")
    assert r.status_code == 403, f"A logged-in user who is not staff must get 403 on /move/ (IsAdminUser), got {r.status_code}."
    item.refresh_from_db()
    assert item.quantity == 10 and Movement.objects.count() == 0, "A refused request must change nothing."


def test_api_move_works_and_records_the_user(item, staff):
    r = api_as(staff).post(f"/api/items/{item.pk}/move/", {"delta": -4, "reason": "sale", "note": "web order"}, format="json")
    assert r.status_code == 201, f"A valid move must answer 201, got {r.status_code} {r.content!r}."
    body = r.json()
    assert body["delta"] == -4 and body["quantity"] == 6, f"The answer must show delta -4 and the new quantity 6, got {body!r}."
    movement = Movement.objects.get()
    assert (movement.delta, movement.reason, movement.note, movement.created_by) == (-4, "sale", "web order", staff), (
        "The Movement must store the reason, the note and request.user.")
    assert Item.objects.get(pk=item.pk).quantity == 6, "The stock in the database must be 6."


def test_api_move_oversell_is_409(item, staff):
    r = api_as(staff).post(f"/api/items/{item.pk}/move/", {"delta": -11, "reason": "sale"}, format="json")
    assert r.status_code == 409, f"Not enough stock must give 409 Conflict, got {r.status_code} {r.content!r}."
    assert Item.objects.get(pk=item.pk).quantity == 10 and Movement.objects.count() == 0, "Nothing may change after a refusal."


@pytest.mark.parametrize("payload,field", [
    ({"delta": 0, "reason": "sale"}, "delta"),
    ({"delta": "many", "reason": "sale"}, "delta"),
    ({"delta": 1, "reason": "gift"}, "reason"),
    ({"reason": "sale"}, "delta"),
])
def test_api_move_validates_input(item, staff, payload, field):
    r = api_as(staff).post(f"/api/items/{item.pk}/move/", payload, format="json")
    assert r.status_code == 400, f"{payload} must give 400, got {r.status_code} {r.content!r}."
    assert field in r.json(), f"The error must be listed under {field!r}, got {r.json()!r}."
    assert Movement.objects.count() == 0, "A rejected request must not create a movement."


def test_api_move_unknown_item_is_404(staff):
    r = api_as(staff).post("/api/items/99999/move/", {"delta": 1, "reason": "receive"}, format="json")
    assert r.status_code == 404, f"An unknown id must be 404, got {r.status_code}."

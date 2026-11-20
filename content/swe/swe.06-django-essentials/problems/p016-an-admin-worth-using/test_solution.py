import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse

from django.test.utils import setup_test_environment

from solution import Category, Item

setup_test_environment()      # lets the test client keep r.context (the template context)

User = get_user_model()
CHANGELIST = "/admin/shop/item/"


@pytest.fixture
def items():
    cat = Category.objects.create(name="Writing")
    hats = Category.objects.create(name="Hats")
    return [
        Item.objects.create(name="Pen", sku="WR-001", quantity=10, category=cat),
        Item.objects.create(name="Ink", sku="WR-002", quantity=5, category=cat),
        Item.objects.create(name="Cap", sku="HT-001", quantity=7, category=hats),
    ]


@pytest.fixture
def boss():
    user = User.objects.create_superuser("boss", "b@example.com", "pw")
    c = Client()
    c.force_login(user)
    return c


def staff_with(*codenames):
    """A staff user holding only the given permissions on Item."""
    ContentType.objects.clear_cache()      # the cache would remember ids from rolled-back tests
    ct = ContentType.objects.get_for_model(Item)
    user = User.objects.create_user("staff", password="pw", is_staff=True)
    for code in codenames:
        perm, _ = Permission.objects.get_or_create(codename=code, content_type=ct, defaults={"name": code})
        user.user_permissions.add(perm)
    c = Client()
    c.force_login(user)
    return c


def listed(response):
    return sorted(i.name for i in response.context["cl"].result_list)


def test_changelist_works_for_a_superuser(boss, items):
    r = boss.get(CHANGELIST)
    assert r.status_code == 200, f"The changelist must answer 200 for a superuser, got {r.status_code}. Is the model registered?"
    assert listed(r) == ["Cap", "Ink", "Pen"], f"All three items must be listed, got {listed(r)}."


def test_list_display(boss, items):
    ma = __import__("solution").ItemAdmin
    assert tuple(ma.list_display) == ("name", "sku", "category", "quantity", "discontinued"), (
        f"list_display must be ('name', 'sku', 'category', 'quantity', 'discontinued'), got {tuple(ma.list_display)}.")
    r = boss.get(CHANGELIST)
    assert b"WR-001" in r.content, "The sku column must appear on the changelist page."


def test_search_by_name_and_sku(boss, items):
    assert listed(boss.get(CHANGELIST, {"q": "pen"})) == ["Pen"], "?q=pen must find the Pen by name, in any case."
    assert listed(boss.get(CHANGELIST, {"q": "HT-0"})) == ["Cap"], "?q=HT-0 must find the Cap by its sku: add 'sku' to search_fields."
    assert listed(boss.get(CHANGELIST, {"q": "WR-"})) == ["Ink", "Pen"], "?q=WR- matches two skus."
    assert listed(boss.get(CHANGELIST, {"q": "zzz"})) == [], "A search with no match lists nothing."


def test_filters(boss, items):
    cat_id = items[2].category_id
    assert listed(boss.get(CHANGELIST, {"category__id__exact": cat_id})) == ["Cap"], (
        "list_filter must contain 'category' so that ?category__id__exact=<id> filters.")
    Item.objects.filter(pk=items[0].pk).update(discontinued=True)
    assert listed(boss.get(CHANGELIST, {"discontinued__exact": 1})) == ["Pen"], (
        "list_filter must contain 'discontinued' so that ?discontinued__exact=1 filters.")


def test_quantity_is_shown_but_cannot_be_posted(boss, items):
    pen = items[0]
    url = f"/admin/shop/item/{pen.pk}/change/"
    r = boss.get(url)
    assert r.status_code == 200, f"The change page must answer 200 for a superuser, got {r.status_code}."
    assert "quantity" not in r.context["adminform"].form.fields, "quantity must be in readonly_fields, so it is not a form field."
    assert b"10" in r.content, "The read-only quantity (10) must still be displayed."
    r = boss.post(url, {"name": "Pen 2", "sku": "WR-001", "category": pen.category_id, "quantity": 999})
    assert r.status_code == 302, f"A valid change should redirect, got {r.status_code}."
    pen.refresh_from_db()
    assert pen.name == "Pen 2", "Other fields must still be editable."
    assert pen.quantity == 10, "A posted quantity must be ignored: put 'quantity' in readonly_fields."


def test_action_marks_selected_items(boss, items):
    pen, ink, cap = items
    r = boss.post(CHANGELIST, {"action": "mark_discontinued", "_selected_action": [pen.pk, cap.pk]})
    assert r.status_code == 302, f"After the action the admin redirects back to the list (302), got {r.status_code}. Is 'mark_discontinued' in actions?"
    flags = {i.name: i.discontinued for i in Item.objects.all()}
    assert flags == {"Pen": True, "Ink": False, "Cap": True}, f"Only the selected rows must change, got {flags}."


def test_action_is_listed_with_its_description(boss, items):
    r = boss.get(CHANGELIST)
    choices = [value for value, label in r.context["action_form"].fields["action"].choices]
    assert "mark_discontinued" in choices, f"The actions drop-down must contain 'mark_discontinued', got {choices}."


def test_view_only_staff_can_look_but_not_change(items):
    c = staff_with("view_item")
    pen = items[0]
    assert c.get(CHANGELIST).status_code == 200, "A user with view_item may open the changelist."
    url = f"/admin/shop/item/{pen.pk}/change/"
    assert c.get(url).status_code == 200, "A user with view_item may open the change page (read-only)."
    r = c.post(url, {"name": "Hacked", "sku": "WR-001", "category": pen.category_id})
    assert r.status_code == 403, f"A POST without change_item permission must be 403, got {r.status_code}."
    pen.refresh_from_db()
    assert pen.name == "Pen", "The item must not change."


def test_staff_without_permission_gets_403(items):
    c = staff_with()
    assert c.get(CHANGELIST).status_code == 403, "A staff user with no permission on Item gets 403 on the changelist."


def test_anonymous_is_sent_to_the_login(items):
    r = Client().get(CHANGELIST)
    assert r.status_code == 302 and "/admin/login/" in r["Location"], (
        f"An anonymous visitor must be redirected to /admin/login/, got {r.status_code} {r.get('Location')}. "
        "Keep path('admin/', admin.site.urls) in urlpatterns.")

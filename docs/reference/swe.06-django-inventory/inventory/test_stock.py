from unittest import mock

from django.contrib.auth.models import Permission, User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Category, Product, StockMovement
from .services import InsufficientStock, record_movement

RECEIVE, SALE = StockMovement.Reason.RECEIVE, StockMovement.Reason.SALE


class StockServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("worker", password="pw-worker-123")
        cat = Category.objects.create(name="Tools")
        self.product = Product.objects.create(name="Hammer", sku="HM-1", category=cat, price="12.00", quantity=10)

    def test_receiving_adds_stock_and_records_who(self):
        m = record_movement(self.product, 5, RECEIVE, user=self.user, note="delivery")
        self.assertEqual(self.product.quantity, 15, "the in-memory product should show the new stock")
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 15)
        self.assertEqual((m.delta, m.created_by), (5, self.user))

    def test_selling_the_last_unit_is_allowed(self):
        record_movement(self.product, -10, SALE)
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 0)

    def test_overselling_is_refused_and_leaves_no_trace(self):
        with self.assertRaises(InsufficientStock) as ctx:
            record_movement(self.product, -11, SALE)
        self.assertEqual((ctx.exception.wanted, ctx.exception.available), (11, 10))
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 10, "stock must be unchanged")
        self.assertEqual(StockMovement.objects.count(), 0, "no movement row for a refused sale")

    def test_a_failure_after_the_update_rolls_the_stock_back(self):
        with mock.patch.object(StockMovement.objects, "create", side_effect=RuntimeError("disk full")):
            with self.assertRaises(RuntimeError):
                record_movement(self.product, -3, SALE)
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 10, "atomic() should undo the UPDATE")

    def test_zero_movement_is_a_programming_error(self):
        with self.assertRaises(ValueError):
            record_movement(self.product, 0, RECEIVE)

    def test_database_rejects_zero_delta_even_without_the_service(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            StockMovement.objects.create(product=self.product, delta=0, reason=RECEIVE)

    def test_stock_equals_start_plus_sum_of_movements(self):
        for delta in (4, -3, 20, -7):
            record_movement(self.product, delta, RECEIVE if delta > 0 else SALE)
        total = sum(m.delta for m in StockMovement.objects.all())
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 10 + total)


class MovementApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Tools")
        cls.product = Product.objects.create(name="Saw", sku="SW-1", category=cat, price="20.00", quantity=3, reorder_level=5)
        Product.objects.create(name="Nails", sku="NL-1", category=cat, price="1.00", quantity=500, reorder_level=50)
        cls.clerk = User.objects.create_user("clerk", password="pw-clerk-123")
        cls.clerk.user_permissions.add(Permission.objects.get(codename="add_stockmovement"))
        cls.url = f"/api/products/{cls.product.pk}/movements/"

    def test_anonymous_cannot_record(self):
        r = APIClient().post(self.url, {"delta": 1, "reason": "receive"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_user_without_permission_cannot_record(self):
        api = APIClient()
        api.force_authenticate(User.objects.create_user("plain", password="pw-plain-123"))
        self.assertEqual(api.post(self.url, {"delta": 1, "reason": "receive"}, format="json").status_code, 403)

    def test_clerk_records_a_sale(self):
        api = APIClient(); api.force_authenticate(self.clerk)
        r = api.post(self.url, {"delta": -2, "reason": "sale", "note": "web order"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 1)
        self.assertEqual(StockMovement.objects.get().created_by, self.clerk)

    def test_overselling_returns_409_and_changes_nothing(self):
        api = APIClient(); api.force_authenticate(self.clerk)
        r = api.post(self.url, {"delta": -4, "reason": "sale"}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertIn("only 3 in stock", r.json()["detail"])
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 3)

    def test_bad_input_returns_400(self):
        api = APIClient(); api.force_authenticate(self.clerk)
        r = api.post(self.url, {"delta": 0, "reason": "gift"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(sorted(r.json()), ["delta", "reason"])

    def test_low_stock_list_is_correct_and_cheap(self):
        with self.assertNumQueries(2):                       # COUNT + SELECT (category joined)
            r = APIClient().get("/api/products/low-stock/")
        self.assertEqual([p["sku"] for p in r.json()["results"]], ["SW-1"])


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("boss", password="pw-boss-12345")
        cat = Category.objects.create(name="Tools")
        cls.product = Product.objects.create(name="Saw", sku="SW-1", category=cat, price="20.00", quantity=3)

    def setUp(self):
        self.client.force_login(self.admin)

    def test_quantity_is_not_editable_in_the_admin(self):
        r = self.client.get(reverse("admin:inventory_product_change", args=[self.product.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('name="quantity"', r.content.decode(), "quantity must be read-only")
        before = self.product.quantity
        self.client.post(reverse("admin:inventory_product_change", args=[self.product.pk]),
                         {"name": "Saw", "sku": "SW-1", "category": self.product.category_id, "price": "20.00",
                          "reorder_level": 5, "quantity": 999, "movements-TOTAL_FORMS": 0, "movements-INITIAL_FORMS": 0})
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, before, "a forged quantity must be ignored")

    def test_receive_action_goes_through_the_service(self):
        r = self.client.post(reverse("admin:inventory_product_changelist"),
                             {"action": "receive_10", "_selected_action": [self.product.pk]})
        self.assertEqual(r.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 13)
        self.assertEqual(StockMovement.objects.get().created_by, self.admin)

    def test_movements_cannot_be_added_or_deleted_even_by_a_superuser(self):
        self.assertEqual(self.client.get(reverse("admin:inventory_stockmovement_add")).status_code, 403)
        m = record_movement(self.product, 1, RECEIVE)
        self.assertEqual(self.client.post(reverse("admin:inventory_stockmovement_delete", args=[m.pk]), {"post": "yes"}).status_code, 403)
        self.assertTrue(StockMovement.objects.filter(pk=m.pk).exists())

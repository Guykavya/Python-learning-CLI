from decimal import Decimal

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .forms import ProductForm
from .models import Category, Product


class ProductModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # runs once for the class; data is shared (and protected from changes) between tests
        cls.cables = Category.objects.create(name="Cables")

    def test_low_stock_uses_reorder_level(self):
        Product.objects.create(name="A", sku="A", category=self.cables, price="1", quantity=2, reorder_level=5)
        Product.objects.create(name="B", sku="B", category=self.cables, price="1", quantity=50, reorder_level=5)
        self.assertEqual([p.sku for p in Product.objects.low_stock()], ["A"])

    def test_is_low_is_inclusive(self):
        p = Product(quantity=5, reorder_level=5)
        self.assertTrue(p.is_low, "quantity == reorder_level should count as low")

    def test_price_must_be_positive_in_the_form(self):
        form = ProductForm({"name": "x", "sku": "x", "category": self.cables.pk, "price": "0", "quantity": 1, "reorder_level": 1})
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)


class ProductViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="Tools")
        for i in range(12):
            Product.objects.create(name=f"Tool {i:02}", sku=f"T-{i:02}", category=cls.cat, price="2.50", quantity=i)
        cls.clerk = User.objects.create_user("clerk", password="pw-clerk-123")
        cls.clerk.user_permissions.add(Permission.objects.get(codename="add_product"))

    def test_list_is_paginated(self):
        r = self.client.get(reverse("inventory:product-list"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context["products"]), 5)
        self.assertContains(r, "Page 1 of 3")

    def test_list_costs_two_queries_whatever_the_size(self):
        # one COUNT for the paginator, one SELECT with the category joined
        with self.assertNumQueries(2):
            self.client.get(reverse("inventory:product-list"))

    def test_search(self):
        r = self.client.get(reverse("inventory:product-list"), {"q": "tool 03"})
        self.assertEqual([p.sku for p in r.context["products"]], ["T-03"])

    def test_anonymous_cannot_create(self):
        url = reverse("inventory:product-create")
        r = self.client.get(url)
        self.assertRedirects(r, f"/accounts/login/?next={url}")

    def test_user_without_permission_gets_403(self):
        self.client.force_login(User.objects.create_user("nope", password="pw-nope-123"))
        self.assertEqual(self.client.get(reverse("inventory:product-create")).status_code, 403)

    def test_clerk_can_create(self):
        self.client.force_login(self.clerk)
        data = {"name": "Plane", "sku": "pl-1", "category": self.cat.pk, "price": "19.90", "quantity": 4, "reorder_level": 2}
        r = self.client.post(reverse("inventory:product-create"), data)
        plane = Product.objects.get(sku="PL-1")                  # the form upper-cased it
        self.assertRedirects(r, plane.get_absolute_url())
        self.assertEqual(plane.price, Decimal("19.90"))

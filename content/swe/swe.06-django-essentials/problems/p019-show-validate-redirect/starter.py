from django import forms
from django.db import models
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template import engines
from django.urls import path
from django.views.decorators.http import require_http_methods


class Item(models.Model):
    name = models.CharField(max_length=50)
    sku = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        app_label = "shop"


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "sku", "price"]


PAGE = '<h1>New item</h1><form method="post">{% csrf_token %}{{ form.as_p }}<button>Save</button></form>'


def render_form(request, form):
    """Render the page with the form (it needs the request for the CSRF token)."""
    from django.http import HttpResponse
    return HttpResponse(engines["django"].from_string(PAGE).render({"form": form}, request))


def item_list(request):
    return JsonResponse({"items": list(Item.objects.order_by("id").values_list("sku", flat=True))})


def item_create(request):
    return render_form(request, ItemForm())       # TODO: handle POST, redirect, 405


urlpatterns = [
    path("items/", item_list, name="item_list"),
    # TODO: path("items/new/", item_create, name="item_create"),
]

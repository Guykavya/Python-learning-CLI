from django.db import models
from django.urls import path, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"


class ItemListView(ListView):
    model = Item
    template_name = "items/list.html"
    ordering = ["name"]


class ItemDetailView(DetailView):
    model = Item
    template_name = "items/detail.html"


class ItemCreateView(CreateView):
    model = Item
    fields = ["name", "quantity"]
    template_name = "items/form.html"
    success_url = reverse_lazy("item_list")


class ItemUpdateView(UpdateView):
    model = Item
    fields = ["name", "quantity"]
    template_name = "items/form.html"
    success_url = reverse_lazy("item_list")


urlpatterns = [
    path("items/", ItemListView.as_view(), name="item_list"),
    path("items/new/", ItemCreateView.as_view(), name="item_create"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path("items/<int:pk>/edit/", ItemUpdateView.as_view(), name="item_update"),
]

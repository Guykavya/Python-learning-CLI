from django.db import models
from django.urls import path, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"


class ItemListView(ListView):
    pass  # TODO: model, template_name, ordering


class ItemDetailView(DetailView):
    pass  # TODO: model, template_name


class ItemCreateView(CreateView):
    pass  # TODO: model, fields, template_name, success_url


class ItemUpdateView(UpdateView):
    pass  # TODO: model, fields, template_name, success_url


urlpatterns = [
    path("items/", ItemListView.as_view(), name="item_list"),
    path("items/new/", ItemCreateView.as_view(), name="item_create"),
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path("items/<int:pk>/edit/", ItemUpdateView.as_view(), name="item_update"),
]

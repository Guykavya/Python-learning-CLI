from django.contrib import admin
from django.db import models
from django.urls import path


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "shop"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=50)
    sku = models.CharField(max_length=20, unique=True)
    quantity = models.IntegerField(default=0)
    discontinued = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        app_label = "shop"

    def __str__(self):
        return self.name


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass  # TODO: list_display, search_fields, list_filter, readonly_fields, actions


admin.site.register(Category)

urlpatterns = [path("admin/", admin.site.urls)]

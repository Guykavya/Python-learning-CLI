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
    list_display = ("name", "sku", "category", "quantity", "discontinued")
    search_fields = ("name", "sku")
    list_filter = ("category", "discontinued")
    readonly_fields = ("quantity",)
    actions = ["mark_discontinued"]

    @admin.action(description="Mark selected items as discontinued")
    def mark_discontinued(self, request, queryset):
        updated = queryset.update(discontinued=True)
        self.message_user(request, f"{updated} item(s) marked as discontinued.")


admin.site.register(Category)

urlpatterns = [path("admin/", admin.site.urls)]

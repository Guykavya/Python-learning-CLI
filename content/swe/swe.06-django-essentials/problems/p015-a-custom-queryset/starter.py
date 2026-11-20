from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        app_label = "shop"


class ItemQuerySet(models.QuerySet):
    pass  # TODO: low_stock(threshold), active(), in_category(slug)


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")

    # TODO: objects = ItemQuerySet.as_manager()

    class Meta:
        app_label = "shop"


urlpatterns = []

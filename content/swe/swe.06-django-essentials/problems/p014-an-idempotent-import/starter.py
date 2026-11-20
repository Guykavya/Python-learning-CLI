from django.db import models, transaction


class Item(models.Model):
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"


def import_items(rows):
    raise NotImplementedError("TODO: return (created, updated)")


urlpatterns = []

from django.conf import settings
from django.db import IntegrityError, models, transaction
from django.db.models import F


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"
        # TODO: a CheckConstraint named "item_quantity_not_negative": quantity >= 0


class Movement(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    delta = models.IntegerField()
    reason = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "shop"


def move_stock(item, delta, reason, user=None):
    raise NotImplementedError("TODO: change the stock and record a Movement, all or nothing")


urlpatterns = []

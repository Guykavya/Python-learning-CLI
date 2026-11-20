from django.conf import settings
from django.db import IntegrityError, models, transaction
from django.db.models import F


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=0), name="item_quantity_not_negative"),
        ]


class Movement(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    delta = models.IntegerField()
    reason = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "shop"


def move_stock(item, delta, reason, user=None):
    if delta == 0:
        raise ValueError("delta must not be 0")
    with transaction.atomic():
        Movement.objects.create(item=item, delta=delta, reason=reason, user=user)
        Item.objects.filter(pk=item.pk).update(quantity=F("quantity") + delta)
        item.refresh_from_db(fields=["quantity"])
        return Movement.objects.filter(item=item).latest("id")


urlpatterns = []

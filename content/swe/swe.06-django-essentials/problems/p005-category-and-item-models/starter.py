from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=60)           # TODO: unique, __str__, ordering

    class Meta:
        app_label = "shop"


class Item(models.Model):
    name = models.CharField(max_length=100)          # TODO: all the other fields

    class Meta:
        app_label = "shop"

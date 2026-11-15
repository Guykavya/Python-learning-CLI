from django.db import migrations


def upper_skus(apps, schema_editor):
    Product = apps.get_model("inventory", "Product")      # the historical model, not the real one
    for product in Product.objects.all():
        if product.sku != product.sku.upper():
            product.sku = product.sku.upper()
            product.save(update_fields=["sku"])


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0002_product_reorder_level"),
    ]

    operations = [
        migrations.RunPython(upper_skus, migrations.RunPython.noop),
    ]

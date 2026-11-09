from sandbox import *


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=80)

    class Meta:
        app_label = "shop"

    def __str__(self):
        return self.name


class Supply(models.Model):
    """Which supplier sells which product, and at what cost (data on the relationship)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="supplies")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplies")
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        app_label = "shop"


def seed():
    """Three categories, six products, some tags."""
    create_tables(Category, Tag, Product, Supplier, Supply)   # the tags join table comes with Product
    tools, office, cables = (Category.objects.create(name=n) for n in ("Tools", "Office", "Cables"))
    sale, new = Tag.objects.create(name="sale"), Tag.objects.create(name="new")
    rows = [("Hammer", tools), ("Saw", tools), ("Stapler", office), ("Pen", office),
            ("HDMI cable", cables), ("USB cable", cables)]
    products = [Product.objects.create(name=n, category=c) for n, c in rows]
    products[0].tags.add(sale)
    products[3].tags.add(sale, new)
    return products

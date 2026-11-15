from django.core.management.base import BaseCommand, CommandError

from inventory.models import Product


class Command(BaseCommand):
    help = "Print the products whose stock is at or below their reorder level."

    def add_arguments(self, parser):
        parser.add_argument("--category", help="only this category name")
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **options):
        qs = Product.objects.low_stock().select_related("category")
        if options["category"]:
            qs = qs.filter(category__name__iexact=options["category"])
            if not qs.exists():
                raise CommandError(f"No low-stock products in category {options['category']!r}.")
        for p in qs.order_by("quantity", "name")[: options["limit"]]:
            self.stdout.write(f"{p.sku:8} {p.name:20} {p.quantity:>4} / {p.reorder_level}")
        self.stdout.write(self.style.SUCCESS("done"))

from decimal import Decimal

from django.contrib import admin, messages
from django.db.models import Count, F

from .models import Category, Product, StockMovement
from .services import InsufficientStock, record_movement


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ("name", "sku", "price")
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "product_count")
    search_fields = ("name",)
    inlines = [ProductInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_products=Count("products"))

    @admin.display(description="Products", ordering="_products")
    def product_count(self, obj):
        return obj._products


class MovementInline(admin.TabularInline):
    """The product's history, shown but never edited."""
    model = StockMovement
    extra = 0
    can_delete = False
    fields = ("created", "delta", "reason", "note", "created_by")
    readonly_fields = fields
    ordering = ("-created", "-id")

    def has_add_permission(self, request, obj=None):
        return False


class LowStockFilter(admin.SimpleListFilter):
    title = "stock level"
    parameter_name = "stock"

    def lookups(self, request, model_admin):
        return [("low", "Low stock"), ("out", "Out of stock")]

    def queryset(self, request, queryset):
        if self.value() == "low":
            return queryset.low_stock()
        if self.value() == "out":
            return queryset.filter(quantity=0)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "quantity", "is_low")
    list_filter = (LowStockFilter, "category")
    search_fields = ("name", "sku")
    list_select_related = ("category",)
    readonly_fields = ("created", "quantity")                  # stock changes only through movements
    autocomplete_fields = ("category",)
    inlines = [MovementInline]
    actions = ["receive_10", "discount_10"]

    @admin.display(description="Low stock?", boolean=True)
    def is_low(self, obj):
        return obj.is_low

    @admin.action(description="Receive 10 units of each selected product")
    def receive_10(self, request, queryset):
        for product in queryset:
            record_movement(product, 10, StockMovement.Reason.RECEIVE, user=request.user, note="Admin quick restock")
        self.message_user(request, f"Received 10 units for {queryset.count()} product(s).", messages.SUCCESS)

    @admin.action(description="Reduce price by 10 percent")
    def discount_10(self, request, queryset):
        updated = queryset.update(price=F("price") * Decimal("0.9"))
        self.message_user(request, f"{updated} price(s) reduced.", messages.SUCCESS)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("created", "product", "delta", "reason", "created_by")
    list_filter = ("reason",)
    list_select_related = ("product", "created_by")
    date_hierarchy = "created"

    # an audit trail: nobody adds, edits or deletes rows here
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

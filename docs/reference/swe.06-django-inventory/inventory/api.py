from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, StockMovementSerializer
from .services import InsufficientStock, record_movement


class CanRecordMovement(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("inventory.add_stockmovement")


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "sku"]
    ordering_fields = ["name", "price", "quantity"]

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        queryset = self.filter_queryset(self.get_queryset().low_stock())
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)

    @action(detail=True, methods=["post"], url_path="movements", permission_classes=[CanRecordMovement])
    def movements(self, request, pk=None):
        product = self.get_object()
        serializer = StockMovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            movement = record_movement(product, data["delta"], data["reason"], user=request.user, note=data.get("note", ""))
        except InsufficientStock as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(StockMovementSerializer(movement).data, status=status.HTTP_201_CREATED)


router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)

from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/new/", views.ProductCreateView.as_view(), name="product-create"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product-update"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product-delete"),
]

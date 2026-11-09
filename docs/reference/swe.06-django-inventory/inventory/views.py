from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ProductForm
from .models import Product


def home(request):
    return HttpResponse("Inventory home")


class ProductListView(ListView):
    model = Product
    paginate_by = 5
    context_object_name = "products"

    def get_queryset(self):
        qs = Product.objects.select_related("category")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        return context


class ProductDetailView(DetailView):
    queryset = Product.objects.select_related("category")


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "inventory.add_product"
    model = Product
    form_class = ProductForm


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "inventory.change_product"
    model = Product
    form_class = ProductForm


class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "inventory.delete_product"
    model = Product
    success_url = reverse_lazy("inventory:product-list")

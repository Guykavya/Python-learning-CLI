from django.contrib import admin
from django.urls import include, path

from inventory.api import router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include(router.urls)),
    path("", include("inventory.urls")),
]

from django.http import HttpResponse, JsonResponse
from django.urls import path


def home(request):
    return HttpResponse("Welcome", content_type="text/plain")


def item_detail(request, pk):
    return JsonResponse({"id": pk, "kind": "item"})


def article_detail(request, slug):
    return JsonResponse({"slug": slug, "title": slug.replace("-", " ").title()})


urlpatterns = [
    path("", home),
    path("items/<int:pk>/", item_detail),
    path("articles/<slug:slug>/", article_detail),
]

from django.http import HttpResponse, JsonResponse
from django.urls import path


def home(request):
    return HttpResponse(status=501)          # TODO


def item_detail(request, pk):
    return HttpResponse(status=501)          # TODO


def article_detail(request, slug):
    return HttpResponse(status=501)          # TODO


urlpatterns = []                              # TODO: three path() entries

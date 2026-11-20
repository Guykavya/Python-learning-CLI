from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path


class Note(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        app_label = "shop"


# --- three views you are given (do not change them) ---------------------------------------------

@login_required
def safe_note(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)     # other people's notes do not exist
    return HttpResponse(note.text)


@login_required
def leaky_note(request, pk):
    note = get_object_or_404(Note, pk=pk)                          # BUG: any logged-in user may read it
    return HttpResponse(note.text)


@login_required
def closed_note(request, pk):
    raise Http404("nobody may read notes")                         # too strict: not even the owner


urlpatterns = [
    path("safe/notes/<int:pk>/", safe_note),
    path("leaky/notes/<int:pk>/", leaky_note),
    path("closed/notes/<int:pk>/", closed_note),
]


# --- your work ------------------------------------------------------------------------------------

def check_owner_only(client, base):
    """Raise AssertionError if the notes under `base` do not follow the rule "only the owner may read a note"."""
    pass      # TODO: two users, one note, one request per user, asserts

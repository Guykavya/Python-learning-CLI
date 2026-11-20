# 403 or redirect?

Chapter section 13.4 and "Try it: 403 or redirect?". Protected views answer an anonymous visitor and a logged-in user without permission **differently**, and two of the tools below do not behave the way their names suggest. Here is a complete program with four views and six requests. For each request write the **status code**, then:

- for a **redirect** (302): a space and the `Location` header, exactly as the test client shows it (the login URL with its `?next=` part);
- for a **200**: a space and the response body;
- for any other status (403): nothing more.

User `ann` has no permissions. User `bob` has only the permission `auth.change_user`. `force_login` skips the password check. Django's default `LOGIN_URL` is `/accounts/login/` (the program does not change it).

```python
import django
from django.conf import settings

settings.configure(
    DEBUG=False,
    SECRET_KEY="demo-key-" + "0" * 40,
    ALLOWED_HOSTS=["testserver"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions"],
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ],
    ROOT_URLCONF=__name__,
    USE_TZ=True,
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Permission, User
from django.core.management import call_command
from django.http import HttpResponse
from django.test import Client
from django.urls import path
from django.views import View


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse("profile")


@permission_required("auth.view_user", raise_exception=True)
def report(request):
    return HttpResponse("report")


@permission_required("auth.view_user")
def export(request):
    return HttpResponse("export")


class PanelView(PermissionRequiredMixin, View):
    permission_required = "auth.change_user"

    def get(self, request):
        return HttpResponse("panel")


urlpatterns = [
    path("profile/", ProfileView.as_view()),
    path("report/", report),
    path("export/", export),
    path("panel/", PanelView.as_view()),
]

call_command("migrate", verbosity=0)
ann = User.objects.create_user("ann", password="pw-ann-12345")
bob = User.objects.create_user("bob", password="pw-bob-12345")
bob.user_permissions.add(Permission.objects.get(codename="change_user"))

anonymous = Client()
as_ann = Client()
as_ann.force_login(ann)
as_bob = Client()
as_bob.force_login(bob)

requests = [
    (anonymous, "/profile/"),
    (as_ann, "/report/"),
    (as_ann, "/export/"),
    (anonymous, "/panel/"),
    (as_ann, "/panel/"),
    (as_bob, "/panel/"),
]
for number, (client, url) in enumerate(requests, 1):
    r = client.get(url)
    if r.status_code == 302:
        detail = r["Location"]
    elif r.status_code == 200:
        detail = r.content.decode()
    else:
        detail = ""
    print(f"{number}: {r.status_code} {detail}".rstrip())
```

Write your answer in `answer.txt`: six lines, `1: ...` to `6: ...`, in the format of the `print` above. Do not run it.

## After you answer

1. Why do requests 2 and 3 differ although both users are logged in and both lack `auth.view_user`? Which argument decides it?
2. What does the `?next=` part do after a successful login, and why is it there?
3. Which tool would you use for "any logged-in user may enter", and which for "only users with the permission"?

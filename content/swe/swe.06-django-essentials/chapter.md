# Chapter 6 (SWE): Django essentials

Flask gave you a small core and let you choose every other part. FastAPI gave you typed, validated, documented JSON APIs. **Django** makes a third choice: it ships almost everything a database-backed web site needs in one framework, designed to work together: an **ORM** (talk to the database with Python classes), **migrations** (change the database safely over time), an automatic **admin site** (a working back office for your data, with no code), **authentication** (users, passwords, sessions, permissions), **forms** with validation, a **template** language, **security defaults** (CSRF, XSS escaping, SQL-injection protection), and a **test framework**. The Django slogan is "the web framework for perfectionists with deadlines", and "batteries included" is the idea behind it.

That is a different trade-off. With Flask you pick and wire parts yourself, so you learn more but write more. With Django the parts are chosen for you, so you write less, but you must learn the Django way. This chapter teaches that way, then adds **Django REST Framework (DRF)**, the standard add-on for building JSON APIs on Django.

By the end you reach two outcomes:

- You can **build a working Django project from an empty folder**: models, migrations, an admin, views and templates, a JSON API with DRF, and tests.
- You can **choose between Django, Flask and FastAPI for a project and defend the choice** with reasons about the job, the team and the data, not with taste.

Prerequisites: swe.02 (HTTP, status codes, REST) and swe.03 (SQL, tables, relationships, the N+1 problem). They are referenced, not re-taught. swe.04 and swe.05 are not required, but we compare to them, and section 19 puts the three side by side.

> **Offline rule for this chapter.** Every runnable example runs on your own computer with **SQLite** and Django's **test client**, which calls your site in the same process with no network and no server. The few steps that need a long-running server are marked **Try it on your machine**. The one place where a server is started for real (section 2.5) starts it, fetches one page and stops it inside the same command, and the output shown is that run. PostgreSQL is described but never required.

Every output block in this chapter was produced by actually running the code above it, with these versions (your patch versions may differ; the behaviour described is stable):

```bash run
python -c "
import sys, django, rest_framework, sqlparse, asgiref
print('python         ', sys.version.split()[0])
print('django         ', django.get_version())
print('djangorestfw   ', rest_framework.VERSION)
print('sqlparse       ', sqlparse.__version__)
print('asgiref        ', asgiref.__version__)
"
```
```text
python          3.14.4
django          6.1.3
djangorestfw    3.18.3
sqlparse        0.6.1
asgiref         3.13.0
```

Two things you will see again and again: a **project** folder called `inventory_site` and an **app** called `inventory`. They are the running example of this chapter and become the inventory app of section 18. Short examples about the ORM run in a one-file "sandbox" (section 6.1) so you can try them without any project.

## Table of contents

1. [Why Django, and the MTV pattern](#1-why-django-and-the-mtv-pattern)
2. [Project and app: startproject, startapp](#2-project-and-app-startproject-startapp)
3. [Settings that matter](#3-settings-that-matter)
4. [URLs and views](#4-urls-and-views)
5. [Templates](#5-templates)
6. [Models and the ORM basics](#6-models-and-the-orm-basics)
7. [Relationships and the N+1 problem](#7-relationships-and-the-n1-problem)
8. [Migrations](#8-migrations)
9. [Writing data safely](#9-writing-data-safely)
10. [The admin site](#10-the-admin-site)
11. [Forms and ModelForms](#11-forms-and-modelforms)
12. [Generic class-based views](#12-generic-class-based-views)
13. [Authentication and permissions](#13-authentication-and-permissions)
14. [Testing Django projects](#14-testing-django-projects)
15. [Django REST Framework basics](#15-django-rest-framework-basics)
16. [Middleware, signals and management commands](#16-middleware-signals-and-management-commands)
17. [Security checklist and deployment](#17-security-checklist-and-deployment)
18. [Project: an admin-driven inventory app, step by step](#18-project-an-admin-driven-inventory-app-step-by-step)
19. [Choosing between Django, Flask and FastAPI](#19-choosing-between-django-flask-and-fastapi)
20. [Common traps](#20-common-traps)
21. [Collected traps](#21-collected-traps)
22. [Summary](#22-summary)

## 1. Why Django, and the MTV pattern

### 1.1 What "batteries included" means

Here is what almost every database-backed web application needs, and the Django piece that covers it:

| The site needs... | Django provides... |
|---|---|
| to map URLs to code | the **URLconf** (`urls.py`) and `path()` |
| to run code per request | **views** (functions or classes) |
| to produce HTML | the **template** language |
| to store data | the **ORM** (`models.py`) |
| to change the database safely | **migrations** |
| to validate user input | **forms** and **model forms** |
| to know who the user is | `django.contrib.auth`, **sessions** |
| to let staff edit data | the **admin** site |
| to resist common attacks | CSRF tokens, auto-escaping, parameterised SQL, clickjacking header |
| to send email, cache, translate | `django.core.mail`, the cache framework, `i18n` |
| to test it all | `TestCase`, the **test client**, a test database |
| to run chores | **management commands** (`manage.py ...`) |

The price is that Django has opinions. Where do models live? In `models.py`. Where do settings live? In one `settings.py`. This is a feature when you work in a team: every Django project looks familiar.

### 1.2 MTV, Django's version of MVC

You may know **MVC** (Model, View, Controller). Django uses different names for nearly the same idea:

| Pattern part | Django name | Job |
|---|---|---|
| Model | **Model** | the data and its rules (`models.py`, the ORM) |
| View (what is shown) | **Template** | how the data looks (HTML with placeholders) |
| Controller (what happens) | **View** | a function that takes a request and returns a response |

So Django's "view" is closer to a *controller*: it decides what to fetch and which template to fill. The part that plays the "front controller" (receives a request and picks the right view) is the **URLconf**.

```text
          browser
             |
        HTTP request
             v
   +--------------------+
   |    URLconf         |   "/products/7/"  ->  product_detail(request, pk=7)
   +--------------------+
             v
   +--------------------+       +-------------+
   |    View            | <---> |   Model     |  ORM <--> database
   +--------------------+       +-------------+
             v
   +--------------------+
   |    Template        |   fills HTML with the data
   +--------------------+
             v
        HTTP response
```

### 1.3 The life of a request

Between the web server and your view, there are more steps than the picture shows. For a normal Django site:

1. The web server (a WSGI or ASGI server, as in swe.02) hands the request to Django.
2. Django builds an `HttpRequest` object.
3. The request goes down through the **middleware** stack (security, sessions, CSRF, authentication, ...). Each layer can look at or change the request, or answer early.
4. The **URL resolver** matches the path to a view.
5. Your **view** runs. It usually reads or writes the database through the ORM and returns an `HttpResponse`.
6. The response goes back **up** through the same middleware, in reverse order, and out to the client.

You will meet each step in this chapter. The important point now: middleware wraps the view like layers of an onion, and the same machinery serves your pages, the admin and your API.

### 1.4 Django in one file

You do not need a project to see Django work. This file configures Django in code, defines a URL and a view, and calls the site with the test client:

```python run
import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,          # "the URLs are in this very file"
    SECRET_KEY="not-a-real-secret-just-for-this-demo-000000000000000",
    ALLOWED_HOSTS=["testserver"],
)
django.setup()

from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.test import Client

def hello(request):
    return HttpResponse("Hello from Django")

def api_ping(request):
    return JsonResponse({"ok": True, "method": request.method})

urlpatterns = [
    path("", hello),
    path("api/ping/", api_ping),
]

client = Client()
r = client.get("/")
print(r.status_code, r["Content-Type"], r.content)
r = client.post("/api/ping/")
print(r.status_code, r.json())
r = client.get("/nope/")
print(r.status_code)
```
```text
200 text/html; charset=utf-8 b'Hello from Django'
200 {'ok': True, 'method': 'POST'}
404
Not Found: /nope/
```

`settings.configure(...)` is what `settings.py` normally does for you. `ROOT_URLCONF=__name__` points at this module (here `__main__`). The line `Not Found: /nope/` is a log message Django prints to the error stream for every 404; it is not part of the response. Real projects never do this; the point is to show how small the core is: **a list of `path()` entries, and functions that take a request and return a response**. Everything else in the chapter builds on those two ideas.

### 1.5 Versions

This chapter runs on the Django shown in the version block above. Django releases a feature version about every eight months, and one in every few is a **long-term support (LTS)** release with security fixes for about three years. For a project that must live for years, pick an LTS or a recent release and read the release notes before upgrading. Always check the version in the docs you read: URLs like `docs.djangoproject.com/en/6.1/` carry it. Old blog posts often show code that no longer works (for example, settings or imports that were removed).

## 2. Project and app: startproject, startapp

### 2.1 Install and check

In a virtual environment (core.13):

```bash
pip install django
python -m django --version
```

This course environment already has Django installed. `django-admin` is the command that creates projects; inside a project you use `python manage.py ...`, the same tool pre-wired to your settings.

### 2.2 `startproject`

```bash run
django-admin startproject inventory_site .
find . -not -name '*.pyc' -not -path './__pycache__*' | sort
```
```text
.
./inventory_site
./inventory_site/asgi.py
./inventory_site/__init__.py
./inventory_site/settings.py
./inventory_site/urls.py
./inventory_site/wsgi.py
./manage.py
```

The final `.` means "create it in the current folder" (without it, Django makes an extra outer folder). What each file does:

| File | Purpose |
|---|---|
| `manage.py` | the command-line tool for this project: run the server, migrate, test, open a shell |
| `inventory_site/settings.py` | **all configuration**: database, installed apps, middleware, secret key |
| `inventory_site/urls.py` | the root **URLconf**: which URL goes where |
| `inventory_site/wsgi.py` | entry point for WSGI servers (gunicorn, uWSGI) |
| `inventory_site/asgi.py` | entry point for ASGI servers (uvicorn, daphne) |
| `inventory_site/__init__.py` | marks the folder as a package |

### 2.3 Project versus app

A **project** is the whole site and its configuration. An **app** is one feature of the site, a Python package with its own models, views and tests. A shop project might have apps `catalog`, `orders`, `accounts`. Good apps are small and have one purpose; the admin, auth and sessions you saw in `INSTALLED_APPS` are apps too.

```bash run
python manage.py startapp inventory
find inventory -not -name '*.pyc' -not -path '*__pycache__*' | sort
```
```text
inventory
inventory/admin.py
inventory/apps.py
inventory/__init__.py
inventory/migrations
inventory/migrations/__init__.py
inventory/models.py
inventory/tests.py
inventory/views.py
```

| File | Purpose |
|---|---|
| `models.py` | the tables (Python classes) |
| `views.py` | the request handlers |
| `admin.py` | how the models look in the admin |
| `apps.py` | the app's configuration class (`InventoryConfig`) |
| `migrations/` | the history of database changes (empty until you run `makemigrations`) |
| `tests.py` | tests (we will turn it into a `tests/` package for bigger apps) |

An app does nothing until you **register** it in `INSTALLED_APPS`. Forgetting this is the most common first mistake (section 20). We add it with a one-line edit:

```bash run
sed -i "s/    'django.contrib.staticfiles',/    'django.contrib.staticfiles',\n    'inventory',/" inventory_site/settings.py
grep -n -A9 "^INSTALLED_APPS" inventory_site/settings.py
```
```text
33:INSTALLED_APPS = [
34-    'django.contrib.admin',
35-    'django.contrib.auth',
36-    'django.contrib.contenttypes',
37-    'django.contrib.sessions',
38-    'django.contrib.messages',
39-    'django.contrib.staticfiles',
40-    'inventory',
41-]
42-
```

(In your editor you just type the line. `inventory` is shorthand for `inventory.apps.InventoryConfig`.)

### 2.4 `manage.py`: the commands you will use

```bash run
python manage.py help --commands
```
```text
changepassword
check
clearsessions
collectstatic
compilemessages
createcachetable
createsuperuser
dbshell
diffsettings
dumpdata
findstatic
flush
inspectdb
loaddata
makemessages
makemigrations
migrate
optimizemigration
remove_stale_contenttypes
runserver
sendtestemail
shell
showmigrations
sqlflush
sqlmigrate
sqlsequencereset
squashmigrations
startapp
startproject
test
testserver
```

The ones that matter in this chapter:

| Command | What it does |
|---|---|
| `runserver` | development server with auto-reload |
| `check` | find mistakes in the configuration (`check --deploy` for production) |
| `makemigrations` | write migration files from your model changes |
| `migrate` | apply migrations to the database |
| `showmigrations`, `sqlmigrate` | see applied migrations, and the SQL a migration would run |
| `shell` | Python shell with Django loaded |
| `createsuperuser` | make an admin account |
| `test` | run the tests |
| `startapp`, `startproject` | scaffolding |
| `dumpdata`, `loaddata` | export and import rows as JSON |
| `collectstatic` | gather static files for deployment |

```bash run
python manage.py check
```
```text
System check identified no issues (0 silenced).
```

`check` found no problems. Run it often; it is fast.

### 2.5 `runserver`

`python manage.py runserver` starts the development server on `http://127.0.0.1:8000/`, reloads when you save a file and shows detailed error pages while `DEBUG = True`. It is **only** for development. The next command starts it, fetches the home page and stops it, so you can see real output.

```bash run
python manage.py runserver --noreload 8123 > server.log 2>&1 &
SERVER=$!
sleep 4
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8123/
curl -s http://127.0.0.1:8123/ | grep -o "<title>[^<]*</title>" | head -1
kill $SERVER
wait $SERVER 2>/dev/null
grep -v "^$" server.log | sed 's/^\[[^]]*\] //'
```
```text
HTTP 200
<title>The install worked successfully! Congratulations!</title>
"GET / HTTP/1.1" 200 12149
"GET / HTTP/1.1" 200 12149
```

A fresh project answers `200` with the "The install worked successfully! Congratulations!" page. (The exact log lines and the time stamps in them depend on your machine and version.)

> **Try it on your machine**
>
> ```bash
> python manage.py runserver
> ```
>
> Open `http://127.0.0.1:8000/` in a browser. Change a file and save: the server restarts by itself. Press Ctrl+C to stop. `runserver 0.0.0.0:8000` listens on all network interfaces (only on a trusted network, and it needs `ALLOWED_HOSTS` set, section 3).

## 3. Settings that matter

`settings.py` is a normal Python module; Django reads the UPPERCASE names. `python manage.py diffsettings` prints every setting that differs from Django's defaults, which is a quick way to see what your project changed (the `SECRET_KEY` and `DATABASES` lines are left out here to keep it short; a `###` at the end of a line means the setting does not exist in Django's global defaults). The generated project has a handful of settings you must understand:

```bash run
python manage.py diffsettings | grep -E "^(ALLOWED_HOSTS|DEBUG|INSTALLED_APPS|ROOT_URLCONF|USE_TZ|TIME_ZONE|STATIC_URL|WSGI_APPLICATION|MAILERS)" | cut -c1-200
```
```text
DEBUG = True
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'inventory']
MAILERS = {'default': {'BACKEND': 'django.core.mail.backends.console.EmailBackend'}}  ###
ROOT_URLCONF = 'inventory_site.urls'  ###
STATIC_URL = 'static/'
TIME_ZONE = 'UTC'
WSGI_APPLICATION = 'inventory_site.wsgi.application'
```

| Setting | Meaning | Rule |
|---|---|---|
| `SECRET_KEY` | signs sessions, password-reset links, CSRF tokens | **never** commit a real one; load from the environment in production |
| `DEBUG` | detailed error pages, auto-serving static files | **`False` in production**. With `True`, the error page leaks settings and code |
| `ALLOWED_HOSTS` | host names the site may be served on | required when `DEBUG = False`; stops host-header attacks |
| `INSTALLED_APPS` | apps Django loads (models, admin, templates, commands) | register every app, in any order unless they override each other |
| `MIDDLEWARE` | the layers around every request, **order matters** | sessions before auth; do not reorder without reason |
| `ROOT_URLCONF` | the module holding the root `urlpatterns` | |
| `TEMPLATES` | template engines and folders (`APP_DIRS` finds `templates/` inside apps) | |
| `DATABASES` | the database connections; `default` is used unless told otherwise | SQLite for learning, PostgreSQL for production |
| `AUTH_PASSWORD_VALIDATORS` | rules for new passwords | keep them |
| `LANGUAGE_CODE`, `TIME_ZONE`, `USE_TZ` | language and time | keep `USE_TZ = True`: store UTC, convert for display |
| `STATIC_URL` | URL prefix for CSS, JavaScript and images | |

Two details of the current version are worth noticing. There is **no `DEFAULT_AUTO_FIELD` line** any more: since Django 6.0, primary keys of new models default to a 64-bit integer (`BigAutoField`). Older tutorials tell you to set it. And Django 6.1 adds a **`MAILERS`** setting (visible at the bottom of the generated file) that configures email in one place; before it, you would find several `EMAIL_*` names. Reading the generated `settings.py` of *your* version is the best way to learn what is current.

### 3.1 Secrets and environments

The generated `SECRET_KEY` begins with `django-insecure-` as a warning: it is for development only. A common simple pattern keeps one `settings.py` and reads the dangerous values from the environment:

```python
import os

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]                # missing -> crash at start, on purpose
DEBUG = os.environ.get("DJANGO_DEBUG") == "1"               # off unless explicitly turned on
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
```

Crashing at start when the key is missing is better than running with a default key that anyone can find on GitHub. Bigger projects split settings into `base.py`, `dev.py` and `prod.py` and choose one with the `DJANGO_SETTINGS_MODULE` environment variable. Section 17 returns to this with `check --deploy`.

### 3.2 Reading settings in code

```python
from django.conf import settings

if settings.DEBUG:
    ...
```

Always `from django.conf import settings`, never `import inventory_site.settings`. The first form respects overrides (for example in tests) and the second does not.

## 4. URLs and views

### 4.1 Function views

A **view** takes an `HttpRequest` and returns an `HttpResponse`. We write the first real views of the inventory site and give the app its own URLconf:

```python
# inventory/views.py
from django.http import HttpResponse, JsonResponse, Http404

PRODUCTS = {1: "Keyboard", 2: "Monitor", 3: "USB cable"}   # fake data until section 6


def home(request):
    return HttpResponse("Inventory home")


def product_detail(request, product_id):
    name = PRODUCTS.get(product_id)
    if name is None:
        raise Http404("No such product")
    return JsonResponse({"id": product_id, "name": name})
```

```python
# inventory/urls.py
from django.urls import path

from . import views

app_name = "inventory"          # the namespace used by reverse() and {% url %}

urlpatterns = [
    path("", views.home, name="home"),
    path("products/<int:product_id>/", views.product_detail, name="product-detail"),
]
```

And the project URLconf includes it:

```python
# inventory_site/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("inventory.urls")),
]
```

To try it without a server, use the test client. We keep a small helper file, `play.py`, that prepares Django and a `client`:

```python
# play.py
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory_site.settings")
django.setup()

from django.test import Client
from django.test.utils import setup_test_environment

setup_test_environment()      # lets the client use the host name "testserver"
client = Client()
```

```python run
from play import client

for url in ["/", "/products/2/", "/products/99/", "/products/abc/"]:
    r = client.get(url)
    print(url, r.status_code, r.content[:40])
```
```text
/ 200 b'Inventory home'
/products/2/ 200 b'{"id": 2, "name": "Monitor"}'
/products/99/ 404 b'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
/products/abc/ 404 b'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
Not Found: /products/99/
Not Found: /products/abc/
```

Look at the last two. `/products/99/` raised `Http404`, which Django turns into a 404 page (a plain page in the test client because we run with the test environment). `/products/abc/` never reached the view: `<int:product_id>` only matches digits, so no URL matched at all, and the result is the same 404.

### 4.2 Path converters

The part in angle brackets is `<converter:name>`. The converter both **matches** and **converts**:

| Converter | Matches | Gives your view |
|---|---|---|
| `str` (default) | any text without `/` | `str` |
| `int` | `0` or a positive integer | `int` |
| `slug` | letters, digits, hyphens, underscores | `str` |
| `uuid` | a formatted UUID | `UUID` |
| `path` | any text, including `/` | `str` |

The view receives them as keyword arguments, so parameter names must match. Negative numbers do not match `int`. For patterns that paths cannot express, `re_path()` accepts regular expressions (core.18), but you rarely need it.

### 4.3 `include`, names, namespaces and `reverse`

Never write URLs by hand in your code or templates. Give each pattern a **name** and build the URL from it:

```python run
from play import client
from django.urls import reverse, resolve

url = reverse("inventory:product-detail", kwargs={"product_id": 3})
print(url)
print(reverse("inventory:home"))
match = resolve("/products/3/")
print(match.view_name, match.kwargs, match.func.__name__)
print(client.get(url).json())
```
```text
/products/3/
/
inventory:product-detail {'product_id': 3} product_detail
{'id': 3, 'name': 'USB cable'}
```

`reverse("namespace:name", kwargs=...)` builds the path; `resolve(path)` goes the other way. If you move the whole app to `/stock/` in the project URLconf, every `reverse()` call and template link keeps working. `app_name = "inventory"` in the app URLconf creates the **namespace**, which prevents two apps that both use the name `home` from clashing. In templates the same thing is `{% url 'inventory:product-detail' product_id=3 %}` (section 5).

### 4.4 What a view can see and return

The `request` object carries everything about the call:

| Attribute | Meaning |
|---|---|
| `request.method` | `"GET"`, `"POST"`, ... |
| `request.GET`, `request.POST` | query-string and form data (`QueryDict`, dictionary-like; `.get("a")`, `.getlist("a")`) |
| `request.body` | raw bytes (use for JSON: `json.loads(request.body)`) |
| `request.headers` | case-insensitive headers |
| `request.user` | the logged-in user or `AnonymousUser` (set by auth middleware) |
| `request.session` | a dictionary stored per visitor |
| `request.path`, `request.get_full_path()` | the URL |
| `request.FILES` | uploaded files |

Useful responses: `HttpResponse`, `JsonResponse`, `HttpResponseRedirect` / `redirect("name")`, `HttpResponseNotFound`, `render(request, "template.html", context)` and `FileResponse`. The shortcut `get_object_or_404(Model, pk=...)` fetches a row or raises `Http404` (section 6.3). The decorator `@require_http_methods(["GET", "POST"])` (or `@require_GET`, `@require_POST`) answers `405` for other methods:

```python run
import play                      # prepares Django (see play.py above)
from django.http import HttpResponse
from django.views.decorators.http import require_POST

@require_POST
def only_post(request):
    return HttpResponse("posted")

from django.test import RequestFactory
rf = RequestFactory()
print(only_post(rf.get("/x/")).status_code)
print(only_post(rf.post("/x/")).status_code)
```
```text
405
200
Method Not Allowed (GET): /x/
```

`RequestFactory` builds a request object without going through URLs and middleware, so you can call a view like a plain function. That is handy for small tests.

### 4.5 Class-based views, the first look

A **class-based view (CBV)** puts one method per HTTP verb in a class. You connect it with `.as_view()`:

```python run
import play                      # prepares Django
from django.http import JsonResponse
from django.views import View
from django.test import RequestFactory

class Ping(View):
    def get(self, request):
        return JsonResponse({"ping": "pong"})

    def post(self, request):
        return JsonResponse({"posted": True}, status=201)

view = Ping.as_view()
rf = RequestFactory()
print(view(rf.get("/")).status_code, view(rf.post("/")).status_code, view(rf.delete("/")).status_code)
```
```text
200 201 405
Method Not Allowed (DELETE): /
```

An unsupported verb gets `405 Method Not Allowed` automatically. Plain `View` classes are not much shorter than functions. Their power appears in **generic views** (`ListView`, `CreateView`, ...), section 12, which do whole CRUD screens in a few lines. Rule of thumb: use a function for something unique, a generic class for standard list/detail/create/update/delete.

### Try it: a greeting view

Write a view `greet` for the URL `greet/<str:name>/` that returns `Hello, <name>!`, and a name `greet` in the `inventory` namespace. What does `reverse("inventory:greet", args=["Ada"])` return?

<details><summary>Answer</summary>

```python
# inventory/views.py
def greet(request, name):
    return HttpResponse(f"Hello, {name}!")

# inventory/urls.py   (add to urlpatterns)
path("greet/<str:name>/", views.greet, name="greet"),
```

`reverse("inventory:greet", args=["Ada"])` returns `/greet/Ada/`. Positional `args` work as well as `kwargs`. Note that `<str:name>` does not match a name with a slash in it, so `/greet/a/b/` is a 404.

</details>

## 5. Templates

### 5.1 The Django template language

A **template** is an HTML file with placeholders. The Django Template Language (DTL) has four building blocks:

| Syntax | Name | Example |
|---|---|---|
| `{{ value }}` | variable | `{{ product.name }}` |
| `{{ value\|filter }}` | filter (transform) | `{{ name\|upper }}`, `{{ price\|floatformat:2 }}` |
| `{% tag %}` | tag (logic) | `{% if %}`, `{% for %}`, `{% url %}`, `{% extends %}` |
| `{# note #}` | comment | |

Dots do lookups in a fixed order: dictionary key, then attribute, then list index. So `{{ product.name }}` works for a dict or an object, and a method is called automatically if it takes no arguments. Templates deliberately have **no arbitrary Python**. This keeps logic in views and makes templates safe to hand to a designer.

You can try the engine alone, without any project:

```python run
import django
from django.conf import settings
settings.configure(TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates"}])
django.setup()

from django.template import Template, Context

t = Template("""\
Hello {{ user.name|upper }}!
{% if items %}You have {{ items|length }} item{{ items|length|pluralize }}:
{% for it in items %}  {{ forloop.counter }}. {{ it.title }} ({{ it.price|floatformat:2 }}){% if forloop.last %} <- last{% endif %}
{% endfor %}{% else %}Your list is empty.
{% endif %}""")

print(t.render(Context({"user": {"name": "ada"}, "items": [
    {"title": "Keyboard", "price": 49.5}, {"title": "Cable", "price": 3}]})))
print(t.render(Context({"user": {"name": "bo"}, "items": []})))
```
```text
Hello ADA!
You have 2 items:
  1. Keyboard (49.50)
  2. Cable (3.00) <- last

Hello BO!
Your list is empty.
```

The `forloop` variable (`counter`, `counter0`, `first`, `last`, `parentloop`) exists inside every `for`. `{% empty %}` is a neat shortcut: `{% for x in xs %}...{% empty %}nothing{% endfor %}`.

### 5.2 Auto-escaping: the built-in XSS defence

Django **escapes** HTML in every variable by default:

```python run
import django
from django.conf import settings
settings.configure(TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates"}])
django.setup()

from django.template import Template, Context
from django.utils.safestring import mark_safe

evil = "<script>alert('hacked')</script>"
print(Template("{{ x }}").render(Context({"x": evil})))
print(Template("{{ x|safe }}").render(Context({"x": evil})))
print(Template("{{ x }}").render(Context({"x": mark_safe("<b>trusted</b>")})))
```
```text
&lt;script&gt;alert(&#x27;hacked&#x27;)&lt;/script&gt;
<script>alert('hacked')</script>
<b>trusted</b>
```

The first line is harmless text the browser shows instead of running it. `|safe` and `mark_safe()` switch escaping off: use them **only** for HTML you wrote yourself, never for anything a user typed. In Flask/Jinja2 (swe.04) autoescape is also on in most setups; the lesson is the same everywhere: if you print user text into HTML, escape it.

### 5.3 Template inheritance

Pages of a site share a frame (header, navigation, footer). A **base template** defines named `{% block %}` holes and child templates fill them:

```html
<!-- inventory/templates/inventory/base.html -->
<!doctype html>
<html>
<head><title>{% block title %}Inventory{% endblock %}</title></head>
<body>
  <nav><a href="{% url 'inventory:home' %}">Home</a></nav>
  <main>{% block content %}{% endblock %}</main>
</body>
</html>
```

```html
<!-- inventory/templates/inventory/product_list.html -->
{% extends "inventory/base.html" %}

{% block title %}Products{% endblock %}

{% block content %}
<h1>Products</h1>
<ul>
{% for p in products %}
  <li><a href="{% url 'inventory:product-detail' product_id=p.id %}">{{ p.name }}</a></li>
{% empty %}
  <li>No products yet.</li>
{% endfor %}
</ul>
{% endblock %}
```

The folder `inventory/templates/inventory/` has the app name twice on purpose: Django searches the `templates/` folder of **every** installed app as one pool, so a plain `product_list.html` in two apps would clash. The inner folder is the namespace.

A view renders it with `render()`:

```python
# inventory/views.py
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render

PRODUCTS = {1: "Keyboard", 2: "Monitor", 3: "USB cable"}   # fake data until section 6


def home(request):
    return HttpResponse("Inventory home")


def product_list(request):
    products = [{"id": pk, "name": name} for pk, name in PRODUCTS.items()]
    return render(request, "inventory/product_list.html", {"products": products})


def product_detail(request, product_id):
    name = PRODUCTS.get(product_id)
    if name is None:
        raise Http404("No such product")
    return JsonResponse({"id": product_id, "name": name})
```

```bash run
cat >> inventory/urls.py <<'EOF'
urlpatterns.append(path("products/", views.product_list, name="product-list"))
EOF
python - <<'EOF'
from play import client
r = client.get("/products/")
print(r.status_code)
print(r.content.decode())
EOF
```
```text
200
<!doctype html>
<html>
<head><title>Products</title></head>
<body>
  <nav><a href="/">Home</a></nav>
  <main>
<h1>Products</h1>
<ul>

  <li><a href="/products/1/">Keyboard</a></li>

  <li><a href="/products/2/">Monitor</a></li>

  <li><a href="/products/3/">USB cable</a></li>

</ul>
</main>
</body>
</html>
```

The `{% url %}` tag built the links from the names, and the loop produced one `<li>` per product. Changing `base.html` changes every page at once.

### 5.4 Static files

CSS, JavaScript and images are **static files**. Put them in `inventory/static/inventory/...`, load them in a template with `{% load static %}` and `<link href="{% static 'inventory/site.css' %}">`. With `DEBUG = True`, `runserver` serves them. In production a web server or a tool such as WhiteNoise serves them after `python manage.py collectstatic` copies everything into one folder (section 17). Files that users upload (profile pictures, invoices) are called **media** and are a separate setting (`MEDIA_ROOT`, `MEDIA_URL`); never mix them with static files.

### Try it: a filter chain

What does `{{ "  Hello World  "|lower|cut:" " }}` print? (`cut` removes the given text; `lower` lowercases. Predict, then check.)

<details><summary>Answer</summary>

```python
import django
from django.conf import settings
settings.configure(TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates"}])
django.setup()
from django.template import Template, Context
print(repr(Template('{{ "  Hello World  "|lower|cut:" " }}').render(Context())))
```

Filters apply from left to right: `lower` gives `"  hello world  "`, then `cut:" "` removes every space, leaving `helloworld`. (Output: `'helloworld'`.) Run it to confirm; if you predicted `hello world`, you remembered `strip` instead of `cut`: `cut` removes the text everywhere, not only at the ends.

</details>


## 6. Models and the ORM basics

### 6.1 The sandbox: try the ORM without a project

A Django **model** is a Python class that describes a table. The **ORM** (Object-Relational Mapper) turns class operations into SQL. You learned the SQL side in swe.03; here we use Django's.

To experiment without creating a project and running migrations, this chapter uses a small helper file, `sandbox.py`. It configures Django with an **in-memory SQLite** database, and gives two helpers: `create_tables(...)` (build the tables for some models; in a real project **migrations** do this, section 8) and `show_queries(...)` (print how many SQL queries ran, and the SQL). Save it next to your experiments:

```python
# sandbox.py
import django
from django.apps import AppConfig
from django.conf import settings


class ShopConfig(AppConfig):
    """A fake app called "shop" so that our models belong to a registered app."""
    name = "sandbox"
    label = "shop"


if not settings.configured:
    settings.configure(
        DEBUG=False,
        SECRET_KEY="sandbox-secret-key-for-demos-only-0000000000000000",
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "sandbox.ShopConfig"],
        USE_TZ=True,
    )
    django.setup()

from django.db import connection, models
from django.test.utils import CaptureQueriesContext


def create_tables(*model_classes):
    """Create one table per model (parents first). Migrations do this in a real project."""
    with connection.schema_editor() as editor:
        for model in model_classes:
            editor.create_model(model)


class show_queries:
    """Context manager: print how many SQL queries ran, and the SQL text."""

    def __init__(self, label=""):
        self.label = label

    def __enter__(self):
        self.ctx = CaptureQueriesContext(connection)
        self.ctx.__enter__()
        return self.ctx

    def __exit__(self, *exc):
        self.ctx.__exit__(*exc)
        n = len(self.ctx.captured_queries)
        print(f"{self.label}{n} quer{'y' if n == 1 else 'ies'}")
        for q in self.ctx.captured_queries:
            print("  ", q["sql"])
```

The small `ShopConfig` class registers a fake app called `shop`. Because our sandbox models do not live inside a real app folder, each declares `class Meta: app_label = "shop"` to say which app it belongs to (reverse relations such as `category.products` only work for models of a registered app). In a real project the app is known from where the file lives, and you never write this line.

### 6.2 A model is a table

```python
# catalog.py
from sandbox import *


class Product(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISCONTINUED = "discontinued", "Discontinued"

    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"
```

Each class attribute that is a `Field` becomes a column. You did not write an `id`: Django adds `id = BigAutoField(primary_key=True)` for you. To see the SQL that Django would run to create the table:

```python run
from catalog import *

with connection.schema_editor(collect_sql=True) as editor:
    editor.create_model(Product)
print("\n".join(editor.collected_sql))
```
```text
CREATE TABLE "shop_product" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "sku" varchar(20) NOT NULL UNIQUE, "price" decimal NOT NULL, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "status" varchar(20) NOT NULL, "notes" text NOT NULL, "created" datetime NOT NULL);
```

Compare with the Python: `CharField(max_length=100)` became `varchar(100)`, `PositiveIntegerField` got a `CHECK (... >= 0)` constraint, `unique=True` became a `UNIQUE` column, and `TextChoices` stored the short value (`'active'`) in the column. The table name `shop_product` is `<app label>_<model name in lowercase>`.

The fields you will use most:

| Field | Python type | Notes |
|---|---|---|
| `CharField(max_length=...)` | `str` | short text, `max_length` required |
| `TextField()` | `str` | long text |
| `IntegerField`, `PositiveIntegerField`, `BigIntegerField` | `int` | |
| `DecimalField(max_digits, decimal_places)` | `Decimal` | **money**: never use `FloatField` |
| `BooleanField()` | `bool` | |
| `DateField`, `DateTimeField`, `TimeField` | `date`, `datetime`, `time` | `auto_now_add=True` sets it on creation, `auto_now=True` on every save |
| `EmailField`, `URLField`, `SlugField` | `str` | a `CharField` plus validation |
| `UUIDField`, `JSONField`, `FileField`, `ImageField` | | |
| `ForeignKey`, `ManyToManyField`, `OneToOneField` | model instances | relationships (section 7) |

Options that every field accepts, and the one confusion to avoid:

| Option | Meaning |
|---|---|
| `null=True` | the **database** column may hold `NULL` |
| `blank=True` | the **form validation** accepts an empty value |
| `default=` | value used when none is given (a value or a callable such as `timezone.now`) |
| `unique=True` | no two rows may have the same value |
| `db_index=True` | build an index on the column |
| `choices=` | a fixed list of allowed values (shown as a select box in forms and the admin) |
| `validators=[...]` | extra checks, run by forms and by `full_clean()` |
| `verbose_name`, `help_text` | labels for forms and the admin |

`null` is about **storage**, `blank` is about **validation**. For text fields, Django's convention is to avoid `null=True` and store the empty string `""` instead, so "no value" has only one representation. That is why `notes` above has `blank=True` and no `null`. For non-text fields (numbers, dates) an optional value needs **both**: `null=True, blank=True`.

`class Meta` holds options for the table: `ordering` (default sort), `verbose_name`, `constraints`, `indexes`, `unique_together` (older; prefer `UniqueConstraint`). Always define `__str__`: it is what the admin, the shell and error messages print.

### 6.3 Creating, saving and reading rows

Every model has a **manager**, `Model.objects`, the door to the table. A **QuerySet** is a (lazy) collection of rows.

```python run
from catalog import *

create_tables(Product)

p = Product(name="Keyboard", sku="KB-1", price="49.90", quantity=10)   # not saved yet
print("before save:", p.pk)
p.save()                                                               # INSERT
print("after save: ", p.pk)

Product.objects.create(name="Monitor", sku="MN-1", price="189.00", quantity=3)
Product.objects.create(name="USB cable", sku="CB-1", price="3.50", quantity=120)
Product.objects.create(name="Old mouse", sku="MS-0", price="9.00", quantity=0,
                       status=Product.Status.DISCONTINUED)

print(Product.objects.count())
print(Product.objects.all())                 # a QuerySet; the default ordering is by name
kb = Product.objects.get(sku="KB-1")         # exactly one row, or an exception
print(kb, kb.price, type(kb.price).__name__, kb.created.tzinfo)

try:
    Product.objects.get(sku="ZZ-9")
except Product.DoesNotExist as e:
    print("DoesNotExist:", e)

try:
    Product.objects.get(quantity__gt=-1)
except Product.MultipleObjectsReturned as e:
    print("MultipleObjectsReturned:", e)

kb.quantity = 8
kb.save()                                    # UPDATE the row
print(Product.objects.get(pk=kb.pk).quantity)
kb.delete()                                  # DELETE
print(Product.objects.count())
```
```text
before save: None
after save:  1
4
<QuerySet [<Product: Keyboard (KB-1)>, <Product: Monitor (MN-1)>, <Product: Old mouse (MS-0)>, <Product: USB cable (CB-1)>]>
Keyboard (KB-1) 49.90 Decimal UTC
DoesNotExist: Product matching query does not exist.
MultipleObjectsReturned: get() returned more than one Product -- it returned 4!
8
3
```

`get()` is for "I expect exactly one", and it raises `DoesNotExist` (zero rows) or `MultipleObjectsReturned` (more than one), which are attributes of the model class. In a view you rarely catch them by hand: `get_object_or_404(Product, pk=7)` returns the row or raises `Http404`. Prices come back as `Decimal` and the creation time is timezone-aware (UTC), because `USE_TZ = True`.

### 6.4 Filtering and lookups

`filter()` and `exclude()` return a new QuerySet, so you can chain them. Field conditions use **double underscores**: `field__lookup=value`.

```python run
from catalog import *

create_tables(Product)
for name, sku, price, qty in [("Keyboard", "KB-1", "49.90", 10), ("Monitor", "MN-1", "189.00", 3),
                              ("USB cable", "CB-1", "3.50", 120), ("USB hub", "HB-1", "21.00", 0),
                              ("Mouse pad", "MP-1", "5.00", 40)]:
    Product.objects.create(name=name, sku=sku, price=price, quantity=qty)

P = Product.objects
print("exact      ", P.filter(sku="KB-1"))
print("icontains  ", P.filter(name__icontains="usb"))
print("startswith ", P.filter(name__startswith="M"))
print("gt         ", P.filter(price__gt=20))
print("range      ", P.filter(price__range=(5, 50)))
print("in         ", P.filter(sku__in=["KB-1", "CB-1"]))
print("isnull     ", P.filter(notes__isnull=True).count(), "(notes is never NULL here)")
print("chained    ", P.filter(name__icontains="usb").exclude(quantity=0))
print("order_by   ", P.order_by("-price")[:2])
print("first/last ", P.order_by("price").first(), "|", P.order_by("price").last())
print("exists     ", P.filter(quantity=0).exists(), P.filter(price__gt=1000).exists())
print("values_list", list(P.values_list("sku", flat=True)))
print("values     ", list(P.filter(sku="MN-1").values("name", "price")))
```
```text
exact       <QuerySet [<Product: Keyboard (KB-1)>]>
icontains   <QuerySet [<Product: USB cable (CB-1)>, <Product: USB hub (HB-1)>]>
startswith  <QuerySet [<Product: Monitor (MN-1)>, <Product: Mouse pad (MP-1)>]>
gt          <QuerySet [<Product: Keyboard (KB-1)>, <Product: Monitor (MN-1)>, <Product: USB hub (HB-1)>]>
range       <QuerySet [<Product: Keyboard (KB-1)>, <Product: Mouse pad (MP-1)>, <Product: USB hub (HB-1)>]>
in          <QuerySet [<Product: Keyboard (KB-1)>, <Product: USB cable (CB-1)>]>
isnull      0 (notes is never NULL here)
chained     <QuerySet [<Product: USB cable (CB-1)>]>
order_by    <QuerySet [<Product: Monitor (MN-1)>, <Product: Keyboard (KB-1)>]>
first/last  USB cable (CB-1) | Monitor (MN-1)
exists      True False
values_list ['KB-1', 'MN-1', 'MP-1', 'CB-1', 'HB-1']
values      [{'name': 'Monitor', 'price': Decimal('189.00')}]
```

The lookups you will use daily:

| Lookup | Meaning |
|---|---|
| `exact` (default), `iexact` | equals (case-insensitive) |
| `contains`, `icontains` | substring (`LIKE '%x%'`) |
| `startswith`, `endswith` (and `i` versions) | |
| `gt`, `gte`, `lt`, `lte` | comparisons |
| `in` | value in a list |
| `range` | between two values, inclusive |
| `isnull` | `IS NULL` / `IS NOT NULL` |
| `year`, `month`, `date` | parts of a date field (`created__year=2026`) |

`.first()` and `.last()` return one object or `None` (not an exception). `.values()` gives dictionaries, `.values_list()` gives tuples, and `flat=True` a flat list of one column: use them when you need data and not full objects.

#### OR, NOT and column-to-column comparisons

All the keyword arguments in one `filter()` are combined with AND. For OR and NOT, wrap conditions in **`Q` objects**. To compare a column with another column, or to update a value from itself, use **`F` expressions**:

```python run
from catalog import *
from django.db.models import F, Q

create_tables(Product)
for name, sku, price, qty in [("Keyboard", "KB-1", "49.90", 10), ("Monitor", "MN-1", "189.00", 3),
                              ("USB cable", "CB-1", "3.50", 120), ("USB hub", "HB-1", "21.00", 0)]:
    Product.objects.create(name=name, sku=sku, price=price, quantity=qty)

P = Product.objects
print("OR  :", P.filter(Q(name__startswith="K") | Q(price__gt=100)))
print("NOT :", P.filter(~Q(name__icontains="usb")))
print("mix :", P.filter(Q(quantity=0) | Q(price__lt=5), name__icontains="usb"))

# F: compare a column with another column / compute inside the database
print("qty > price/10:", P.filter(quantity__gt=F("price") / 10))

with show_queries("raise price 10%: "):
    P.filter(sku="CB-1").update(price=F("price") * 11 / 10)
print(P.get(sku="CB-1").price)
```
```text
OR  : <QuerySet [<Product: Keyboard (KB-1)>, <Product: Monitor (MN-1)>]>
NOT : <QuerySet [<Product: Keyboard (KB-1)>, <Product: Monitor (MN-1)>]>
mix : <QuerySet [<Product: USB cable (CB-1)>, <Product: USB hub (HB-1)>]>
qty > price/10: <QuerySet [<Product: Keyboard (KB-1)>, <Product: USB cable (CB-1)>]>
raise price 10%: 1 query
   UPDATE "shop_product" SET "price" = (CAST(((CAST(("shop_product"."price" * 11) AS NUMERIC)) / 10) AS NUMERIC)) WHERE "shop_product"."sku" = 'CB-1'
3.85
```

The `update()` with `F("price")` ran **one** `UPDATE ... SET price = price * 11 / 10` inside the database. The alternative, `p = get(...); p.price = p.price * 1.1; p.save()`, reads the value into Python and writes it back, and if two requests do it at once, one change is lost (a **race condition**). When many users can change the same number (stock levels, counters), use `F()`.

### 6.5 Aggregation and annotation

`aggregate()` collapses the whole QuerySet into one result. `annotate()` adds a computed value to **each row**, and combined with `values()` it is GROUP BY:

```python run
from catalog import *
from django.db.models import Avg, Count, F, Max, Sum

create_tables(Product)
for name, sku, price, qty, st in [("Keyboard", "KB-1", "49.90", 10, "active"), ("Monitor", "MN-1", "189.00", 3, "active"),
                                  ("USB cable", "CB-1", "3.50", 120, "active"), ("Old mouse", "MS-0", "9.00", 0, "discontinued"),
                                  ("Dock", "DK-0", "99.00", 2, "discontinued")]:
    Product.objects.create(name=name, sku=sku, price=price, quantity=qty, status=st)

P = Product.objects
print(P.aggregate(n=Count("id"), cheapest=Max("price"), average=Avg("price")))

stock_value = P.annotate(value=F("price") * F("quantity")).order_by("-value")
for p in stock_value:
    print(f"{p.name:10} {p.value}")

print(P.aggregate(total=Sum(F("price") * F("quantity"))))

per_status = P.values("status").annotate(n=Count("id"), units=Sum("quantity")).order_by("status")
print(list(per_status))
```
```text
{'n': 5, 'cheapest': Decimal('189'), 'average': Decimal('70.0800000000000')}
Monitor    567
Keyboard   499
USB cable  420
Dock       198
Old mouse  0
{'total': Decimal('1684')}
[{'status': 'active', 'n': 3, 'units': 133}, {'status': 'discontinued', 'n': 2, 'units': 2}]
```

Read the last one as SQL: `SELECT status, COUNT(id), SUM(quantity) FROM product GROUP BY status`. The `.values("status")` before `.annotate()` chooses the grouping column; the order matters (`.annotate().values()` means something different: values of a per-row annotation). Django's `Meta.ordering` (`name` here) is not added to the `GROUP BY`, but a manual `.order_by("name")` on such a query would be, and would split the groups per name, so only order by grouped columns or aggregates.

### 6.6 QuerySets are lazy (and cached)

Building a QuerySet does **not** touch the database. It runs when you *use* the result: iterate, `list()`, `len()`, `bool()`, index a single item, or call `count()`, `get()`, `exists()`, `first()`, or `aggregate()`.

```python run
from catalog import *

create_tables(Product)
for i in range(5):
    Product.objects.create(name=f"Item {i}", sku=f"S{i}", price="1.00", quantity=i)

with show_queries("A  building: "):
    qs = Product.objects.filter(quantity__gt=1).order_by("name")   # nothing runs here
    qs = qs.exclude(sku="S4")

with show_queries("B  first loop: "):
    names = [p.name for p in qs]
with show_queries("C  second loop (cached): "):
    names2 = [p.name for p in qs]

with show_queries("D  len() then count(): "):
    fresh = Product.objects.filter(quantity__gt=1)
    print(len(fresh))        # loads all the rows into the cache
    print(fresh.count())     # served from the cache now
with show_queries("E  count() only: "):
    print(Product.objects.filter(quantity__gt=1).count())
with show_queries("F  exists() vs bool(): "):
    print(Product.objects.filter(quantity__gt=1).exists())
```
```text
A  building: 0 queries
B  first loop: 1 query
   SELECT "shop_product"."id", "shop_product"."name", "shop_product"."sku", "shop_product"."price", "shop_product"."quantity", "shop_product"."status", "shop_product"."notes", "shop_product"."created" FROM "shop_product" WHERE ("shop_product"."quantity" > 1 AND NOT ("shop_product"."sku" = 'S4')) ORDER BY "shop_product"."name" ASC
C  second loop (cached): 0 queries
3
3
D  len() then count(): 1 query
   SELECT "shop_product"."id", "shop_product"."name", "shop_product"."sku", "shop_product"."price", "shop_product"."quantity", "shop_product"."status", "shop_product"."notes", "shop_product"."created" FROM "shop_product" WHERE "shop_product"."quantity" > 1 ORDER BY "shop_product"."name" ASC
3
E  count() only: 1 query
   SELECT COUNT(*) AS "__count" FROM "shop_product" WHERE "shop_product"."quantity" > 1
True
F  exists() vs bool(): 1 query
   SELECT 1 AS "a" FROM "shop_product" WHERE "shop_product"."quantity" > 1 LIMIT 1
```

Notice: **A** runs 0 queries; **B** runs 1; **C** runs 0 because a QuerySet keeps its result after the first evaluation. In **E**, `count()` asks the database for `COUNT(*)` and loads no rows; use it when you only need the number, and `exists()` when you only need yes or no. Calling `len(qs)` loads every row just to count them, a common waste on big tables.

One more detail: slicing (`qs[:10]`) becomes `LIMIT`, and `qs[0]` runs a query with `LIMIT 1`. Negative indexes are not supported (use `.last()` or reverse the order).

### Try it: how many queries?

```python
qs = Product.objects.filter(quantity__gt=0)
a = qs.count()
b = len(qs)
c = len(qs)
```

How many SQL queries run for these three lines? Write your answer, then check.

<details><summary>Answer</summary>

Two. `qs.count()` runs one `SELECT COUNT(*)` (the QuerySet is not loaded yet). `len(qs)` loads all rows (query two) and caches them. The second `len(qs)` uses the cache. If you had written `len(qs)` first and `count()` after it, it would be one query, because `count()` reuses a loaded cache.

</details>

### Try it: null versus blank

You add `ordered_on = models.DateField(blank=True)` to a model, then try `Product.objects.create(name="x", sku="y", price=1)` in the shell. What happens, and what is the fix?

<details><summary>Answer</summary>

The database column is `NOT NULL` (no `null=True`), and `create()` does not run form validation, so `blank=True` does not help: Django tries to insert `NULL`, and SQLite raises `IntegrityError: NOT NULL constraint failed`. For an optional date you need `DateField(null=True, blank=True)`. `blank` only affects forms, `full_clean()` and the admin; `null` controls the column.

</details>

## 7. Relationships and the N+1 problem

### 7.1 `ForeignKey`: many rows point to one

A **foreign key** is a column that stores the id of a row in another table. In Django you declare it on the "many" side:

```python
# shop.py
from sandbox import *


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=80)

    class Meta:
        app_label = "shop"

    def __str__(self):
        return self.name


class Supply(models.Model):
    """Which supplier sells which product, and at what cost (data on the relationship)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="supplies")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplies")
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        app_label = "shop"


def seed():
    """Three categories, six products, some tags."""
    create_tables(Category, Tag, Product, Supplier, Supply)   # the tags join table comes with Product
    tools, office, cables = (Category.objects.create(name=n) for n in ("Tools", "Office", "Cables"))
    sale, new = Tag.objects.create(name="sale"), Tag.objects.create(name="new")
    rows = [("Hammer", tools), ("Saw", tools), ("Stapler", office), ("Pen", office),
            ("HDMI cable", cables), ("USB cable", cables)]
    products = [Product.objects.create(name=n, category=c) for n, c in rows]
    products[0].tags.add(sale)
    products[3].tags.add(sale, new)
    return products
```

The `category` field creates a column `category_id`. Two arguments are required in practice:

- `on_delete` says what happens to the product when its category is deleted. **`CASCADE`** deletes the products too; **`PROTECT`** refuses to delete the category while products exist (raises `ProtectedError`); **`RESTRICT`** is like `PROTECT` with finer rules; **`SET_NULL`** (needs `null=True`) clears the link; **`SET_DEFAULT`** uses the field default. Choose on purpose: `CASCADE` on the wrong relation silently deletes data.
- `related_name` names the **reverse** accessor on the other side. Without it, Django uses `product_set`. With `related_name="products"` you write `category.products.all()`.

```python run
from shop import *

seed()
tools = Category.objects.get(name="Tools")
hammer = Product.objects.get(name="Hammer")

print(hammer.category, hammer.category_id)          # forward: one object
print(list(tools.products.all()))                   # reverse: a manager / QuerySet
print(list(Product.objects.filter(category__name="Cables")))   # filter THROUGH the relation
print(Category.objects.filter(products__name__startswith="S").distinct())
print(Product.objects.filter(category=tools).count())

new_cat = Category.objects.create(name="Garden")
hammer.category = new_cat                           # move it
hammer.save()
print(tools.products.count(), new_cat.products.count())

try:
    new_cat.delete()                                # protected: it has a product
except Exception as e:
    print(type(e).__name__)
```
```text
Tools 1
[<Product: Hammer>, <Product: Saw>]
[<Product: HDMI cable>, <Product: USB cable>]
<QuerySet [<Category: Office>, <Category: Tools>]>
2
1 1
ProtectedError
```

The double underscore works across relations: `category__name` means "the `name` of the related category", and the ORM writes the `JOIN`. `.distinct()` was needed in the second query because joining products can repeat a category once per matching product.

### 7.2 `ManyToManyField`: many to many

A product can have several tags, and a tag belongs to many products. Django creates a hidden **join table** (`shop_product_tags`) for you:

```python run
from shop import *

seed()
pen = Product.objects.get(name="Pen")
sale = Tag.objects.get(name="sale")
print(list(pen.tags.all()), list(sale.products.all()))

pen.tags.remove(sale)
print(list(pen.tags.all()))
pen.tags.set([Tag.objects.get(name="sale")])         # replace the whole set
pen.tags.add(Tag.objects.get(name="new"))            # add (no duplicates)
print(list(pen.tags.all()))
pen.tags.clear()
print(pen.tags.count())
print(list(Product.objects.filter(tags__name="sale")))
```
```text
[<Tag: new>, <Tag: sale>] [<Product: Hammer>, <Product: Pen>]
[<Tag: new>]
[<Tag: new>, <Tag: sale>]
0
[<Product: Hammer>]
```

`add`, `remove`, `set` and `clear` change rows in the join table directly (they do not need `save()`). When the relationship itself carries data, like a supplier's `unit_cost` for a product, define the join table yourself as a normal model (`Supply` above) and use two `ForeignKey`s. Django also supports `ManyToManyField(..., through="Supply")` to keep the convenient `product.suppliers` accessor on top of such a model.

### 7.3 `OneToOneField`

A one-to-one link is a `ForeignKey` with `unique=True`, with a nicer reverse accessor. The classic use is extending a built-in model, such as a `Profile` for each `User`:

```python run
from sandbox import *
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        app_label = "shop"

create_tables(User, Profile)
u = User.objects.create_user("ada", password="s3cret-pass")
Profile.objects.create(user=u, phone="555-0100")
print(u.profile.phone, Profile.objects.get(phone="555-0100").user.username)
```
```text
555-0100 ada
```

For new projects that may need extra user fields, Django's advice is to define a **custom user model** at the very start (section 13), because changing it later is painful.

### 7.4 The N+1 problem, and the two fixes

By default related objects are loaded **lazily**: reading `product.category` runs a query the first time. Printing a list of products with their categories then costs 1 query for the list plus 1 per product. That is the **N+1 problem** from swe.03, and in Django it hides behind innocent-looking attribute access.

```python run
from shop import *

seed()

with show_queries("naive:  "):
    for p in Product.objects.all():
        _ = p.category.name

with show_queries("select_related: "):
    for p in Product.objects.select_related("category"):
        _ = p.category.name

with show_queries("prefetch_related (reverse): "):
    for c in Category.objects.prefetch_related("products"):
        _ = [p.name for p in c.products.all()]
```
```text
naive:  7 queries
   SELECT "shop_product"."id", "shop_product"."name", "shop_product"."category_id" FROM "shop_product" ORDER BY "shop_product"."name" ASC
   SELECT "shop_category"."id", "shop_category"."name" FROM "shop_category" WHERE "shop_category"."id" = 3 LIMIT 21
   SELECT "shop_category"."id", "shop_category"."name" FROM "shop_category" WHERE "shop_category"."id" = 1 LIMIT 21
   SELECT "shop_category"."id", "shop_category"."name" FROM "shop_category" WHERE "shop_category"."id" = 2 LIMIT 21
   SELECT "shop_category"."id", "shop_category"."name" FROM "shop_category" WHERE "shop_category"."id" = 1 LIMIT 21
   SELECT "shop_category"."id", "shop_category"."name" FROM "shop_category" WHERE "shop_category"."id" = 2 LIMIT 21
   SELECT "shop_category"."id", "shop_category"."name" FROM "shop_category" WHERE "shop_category"."id" = 3 LIMIT 21
select_related: 1 query
   SELECT "shop_product"."id", "shop_product"."name", "shop_product"."category_id", "shop_category"."id", "shop_category"."name" FROM "shop_product" INNER JOIN "shop_category" ON ("shop_product"."category_id" = "shop_category"."id") ORDER BY "shop_product"."name" ASC
prefetch_related (reverse): 2 queries
   SELECT "shop_category"."id", "shop_category"."name" FROM "shop_category" ORDER BY "shop_category"."name" ASC
   SELECT "shop_product"."id", "shop_product"."name", "shop_product"."category_id" FROM "shop_product" WHERE "shop_product"."category_id" IN (3, 2, 1) ORDER BY "shop_product"."name" ASC
```

(The SQL lines are shown on purpose: read them.) The two tools:

- **`select_related("category")`** follows **forward** `ForeignKey` / `OneToOne` links with a SQL `JOIN`, loading both objects in one query. Use it when each row has *one* related object.
- **`prefetch_related("products")`** runs a **second query** (`WHERE category_id IN (...)`) and matches the rows in Python. Use it for *many* relations: reverse foreign keys and many-to-many.

Typical combined use on a list screen: `Product.objects.select_related("category").prefetch_related("tags")` is 2 queries for the whole page, whatever the number of products. Two more helpers:

- `Prefetch("products", queryset=Product.objects.filter(...))` prefetches a **filtered** list.
- `.only("name")` / `.defer("notes")` load fewer columns, and `.values()` skips model objects altogether. Use them when rows are wide and you need little.

#### Make N+1 visible, not just fixed

Lists, admin pages and templates are where N+1 lives. During development, count queries in a test (section 14: `assertNumQueries`) or use the `django-debug-toolbar` add-on to see the number per page. A test that says "this page costs 3 queries" turns a silent slowdown into a failing test.

### 7.5 Counting across relations, and the double-join trap

```python run
from shop import *
from django.db.models import Count

seed()
for c in Category.objects.annotate(n=Count("products")).order_by("name"):
    print(c.name, c.n)

# Count across TWO relations at once: joins multiply rows
pen = Product.objects.get(name="Pen")
pen.tags.add(Tag.objects.get(name="new"))
s1, s2 = Supplier.objects.create(name="A"), Supplier.objects.create(name="B")
for s in (s1, s2):
    Supply.objects.create(product=pen, supplier=s, unit_cost="0.40")

row = Product.objects.filter(name="Pen").annotate(tags_n=Count("tags"), supplies_n=Count("supplies")).get()
print("wrong  :", row.tags_n, row.supplies_n)
row = Product.objects.filter(name="Pen").annotate(
    tags_n=Count("tags", distinct=True), supplies_n=Count("supplies", distinct=True)).get()
print("correct:", row.tags_n, row.supplies_n)
```
```text
Cables 2
Office 2
Tools 2
wrong  : 4 4
correct: 2 2
```

The pen has 2 tags (`sale`, `new`) and 2 supplies, but the first query reports `4 4`: SQL joined tags × supplies = 4 rows, then counted each column. Whenever you count two different relations in one query, add `distinct=True`. (If this surprises you, review the part of swe.03 about joins multiplying rows.)

### Try it: count the queries

```python
for supply in Supply.objects.all():
    print(supply.product.category.name)
```

With 3 supplies, how many queries run, and what one line fixes it?

<details><summary>Answer</summary>

One query for the supplies, plus per supply one for `product` and one for `product.category`: 1 + 3 + 3 = 7 (each `supply.product` is loaded separately, even when two supplies share a product). The fix is `Supply.objects.select_related("product__category")`: one query with two joins. The double underscore follows the chain `supply → product → category`.

</details>

### Try it: PROTECT or CASCADE?

An `Order` has many `OrderLine` rows (`ForeignKey` to `Order`), and every line points to a `Product`. Which `on_delete` do you choose for line → order, and for line → product, and why?

<details><summary>Answer</summary>

Line → order: `CASCADE`. A line has no meaning without its order; deleting the order should delete its lines. Line → product: `PROTECT`. Old orders must keep their history, so a product that was ever sold must not be deletable (mark it inactive instead). With `CASCADE` there, deleting a product would silently erase sales history, which is the classic accounting bug.

</details>


## 8. Migrations

### 8.1 What a migration is

Your `models.py` describes the tables you *want*. The database has the tables you *have*. A **migration** is a small Python file that describes one step from the old schema to the new one. Migrations are version control for your database: they live in git next to the code, every developer and every server applies the same steps in the same order, and Django records in a table (`django_migrations`) which steps have already run.

The workflow, always the same three moves:

1. Edit `models.py`.
2. `python manage.py makemigrations` writes a new migration file by comparing your models with the previous migrations.
3. `python manage.py migrate` applies the unapplied migrations to the database.

Let us give the inventory app its first real models (replacing the empty `models.py`):

```python
# inventory/models.py
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField("SKU", max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"
```

```bash run
python manage.py showmigrations inventory
python manage.py makemigrations inventory
```
```text
inventory
 (no migrations)
Migrations for 'inventory':
  inventory/migrations/0001_initial.py
    + Create model Category
    + Create model Product
```

```bash run
cat inventory/migrations/0001_initial.py
```
```text
# Generated by Django 6.1.3 on 2026-11-09 05:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sku', models.CharField(max_length=20, unique=True, verbose_name='SKU')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='inventory.category')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
```

(The date on the first line is machine-specific.) Read a migration like a recipe: `dependencies` says what must run before (here the first one depends on nothing of ours), `operations` is the list of steps (`CreateModel`, later `AddField`, `AlterField`, `RunPython`, ...). You can see the SQL a migration will run without running it:

```bash run
python manage.py sqlmigrate inventory 0001
```
```text
BEGIN;
--
-- Create model Category
--
CREATE TABLE "inventory_category" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(60) NOT NULL UNIQUE);
--
-- Create model Product
--
CREATE TABLE "inventory_product" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "sku" varchar(20) NOT NULL UNIQUE, "price" decimal NOT NULL, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "created" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "inventory_category" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "inventory_product_category_id_c907876e" ON "inventory_product" ("category_id");
COMMIT;
```

Now apply everything. The project also has migrations from Django's own apps (admin, auth, sessions), so `migrate` runs those too:

```bash run
python manage.py migrate
python manage.py showmigrations inventory auth
```
```text
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, inventory, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying inventory.0001_initial... OK
  Applying sessions.0001_initial... OK
inventory
 [X] 0001_initial
auth
 [X] 0001_initial
 [X] 0002_alter_permission_name_max_length
 [X] 0003_alter_user_email_max_length
 [X] 0004_alter_user_username_opts
 [X] 0005_alter_user_last_login_null
 [X] 0006_require_contenttypes_0002
 [X] 0007_alter_validators_add_error_messages
 [X] 0008_alter_user_username_max_length
 [X] 0009_alter_user_last_name_max_length
 [X] 0010_alter_group_name_max_length
 [X] 0011_update_proxy_permissions
 [X] 0012_alter_user_first_name_max_length
```

An `[X]` means applied. After this, `db.sqlite3` exists in the project folder with all the tables.

### 8.2 Changing a model

We want a reorder level per product. Edit `Product`:

```python
# inventory/models.py
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField("SKU", max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)      # NEW
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"
```

```bash run
python manage.py makemigrations inventory
python manage.py migrate inventory
```
```text
Migrations for 'inventory':
  inventory/migrations/0002_product_reorder_level.py
    + Add field reorder_level to product
Operations to perform:
  Apply all migrations: inventory
Running migrations:
  Applying inventory.0002_product_reorder_level... OK
```

The new column needed a value for the rows that already exist, and `default=5` supplied it. If a new field is required (not null) and has **no default**, `makemigrations` cannot decide what to put in old rows, so it stops and asks (in interactive mode) or refuses (with `--noinput`). Your choices: give a `default`, make the field `null=True`, or do it in three migrations (add nullable, backfill, make required). That last pattern is the safe way on big tables that must stay online.

Other changes to remember:

| Change | What Django generates | Care |
|---|---|---|
| add a field | `AddField` | needs a default or `null=True` for existing rows |
| remove a field | `RemoveField` | **data is lost**; back up first |
| rename a field | asks "did you rename it?" and writes `RenameField` | if you answer no, it is remove + add: the data is lost |
| change a type or length | `AlterField` | may fail if existing data does not fit |
| rename a model | `RenameModel` | the table is renamed too |

### 8.3 Data migrations

Sometimes the *data* must change together with the schema: fill a new column from old ones, fix bad values, load starting rows. For that, write a migration with `RunPython`. We will normalise every SKU to upper case. First, some rows with messy SKUs (made through the model, as the app is now at migration 0002):

```bash run
python manage.py shell --no-imports -c "
from inventory.models import Category, Product
c = Category.objects.create(name='Cables')
Product.objects.create(name='HDMI cable', sku='cb-hdmi', category=c, price='7.50', quantity=40)
Product.objects.create(name='USB cable', sku='CB-USB', category=c, price='3.50', quantity=120)
Product.objects.create(name='Aux cable', sku='cb-aux', category=c, price='2.00', quantity=4)
print(sorted(Product.objects.values_list('sku', flat=True)))
"
python manage.py makemigrations inventory --empty --name normalise_skus
```
```text
['CB-USB', 'cb-aux', 'cb-hdmi']
Migrations for 'inventory':
  inventory/migrations/0003_normalise_skus.py
```

Open the empty file and fill it:

```python
# inventory/migrations/0003_normalise_skus.py
from django.db import migrations


def upper_skus(apps, schema_editor):
    Product = apps.get_model("inventory", "Product")      # the historical model, not the real one
    for product in Product.objects.all():
        if product.sku != product.sku.upper():
            product.sku = product.sku.upper()
            product.save(update_fields=["sku"])


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0002_product_reorder_level"),
    ]

    operations = [
        migrations.RunPython(upper_skus, migrations.RunPython.noop),
    ]
```

Two rules for `RunPython`:

- Get models with `apps.get_model(...)`, **never** `from inventory.models import Product`. The migration must see the model *as it was at that point in history*. Today's model may have fields that do not exist yet when this migration runs on a fresh database, and custom methods are not available on historical models.
- Give a reverse function (here `RunPython.noop`, "do nothing") so the migration can be undone. Without one, going backwards raises `IrreversibleError`.

```bash run
python manage.py migrate inventory
python manage.py shell --no-imports -c "
from inventory.models import Product
print(sorted(Product.objects.values_list('sku', flat=True)))
"
```
```text
Operations to perform:
  Apply all migrations: inventory
Running migrations:
  Applying inventory.0003_normalise_skus... OK
['CB-AUX', 'CB-HDMI', 'CB-USB']
```

### 8.4 Going back, and checking

```bash run
python manage.py migrate inventory 0002
python manage.py showmigrations inventory
python manage.py migrate inventory
python manage.py makemigrations --check --dry-run
```
```text
Operations to perform:
  Target specific migration: 0002_product_reorder_level, from inventory
Running migrations:
  Rendering model states... DONE
  Unapplying inventory.0003_normalise_skus... OK
inventory
 [X] 0001_initial
 [X] 0002_product_reorder_level
 [ ] 0003_normalise_skus
Operations to perform:
  Apply all migrations: inventory
Running migrations:
  Applying inventory.0003_normalise_skus... OK
No changes detected
```

`migrate <app> <number>` moves to that point, running reverse steps if needed (the SKUs stay upper case, since `noop` cannot restore what was there). `makemigrations --check` exits with an error code if your models have changes without a migration; put it in your CI (continuous integration) so nobody forgets to commit the file.

### 8.5 Team rules for migrations

- **Commit migration files.** They are part of the code.
- **Never edit or delete a migration that others have applied.** Make a new one. Editing history makes the databases of two developers disagree.
- Two people creating migration `0004` on two branches causes a conflict; fix it with `makemigrations --merge` or by renumbering, then test on a fresh database.
- Long histories can be shortened with `squashmigrations`; do that only when every database is up to date.
- Production: run `migrate` as a separate deployment step, before the new code serves traffic, and test the migration on a copy of the production data when the table is large.
- `sqlmigrate` shows what will run. On a big table, `ALTER TABLE` can lock writes. Read the SQL.

### Try it: the missing default

You add `barcode = models.CharField(max_length=13)` to `Product` with 1,000 existing rows and run `makemigrations`. What does Django ask, and which answer causes the least trouble?

<details><summary>Answer</summary>

It says the field is non-nullable and has no default, and offers: (1) provide a one-off default now, or (2) quit and edit `models.py`. A one-off default (for example `''`) fills the old rows and is not kept in the model, but then 1,000 products share the same fake barcode, which is rarely what you want. Usually better: `barcode = models.CharField(max_length=13, blank=True, default="")` (a real default, text field convention), or `null=True` plus a data migration that computes real barcodes, and a later migration that makes it required.

</details>

## 9. Writing data safely

### 9.1 Bulk operations

`save()` in a loop sends one statement per row. For many rows, use the bulk tools:

```python run
from shop import *

create_tables(Category, Tag, Product, Supplier, Supply)
cat = Category.objects.create(name="Bulk")

with show_queries("save() loop: "):
    for i in range(3):
        Product.objects.create(name=f"loop-{i}", category=cat)

objs = [Product(name=f"bulk-{i}", category=cat) for i in range(1000)]
with CaptureQueriesContext(connection) as ctx:
    Product.objects.bulk_create(objs, batch_size=500)
print("bulk_create 1000 rows:", len(ctx.captured_queries), "queries")

with CaptureQueriesContext(connection) as ctx:
    n = Product.objects.filter(name__startswith="bulk-").update(name="renamed")
print("update():", n, "rows,", len(ctx.captured_queries), "query")

with CaptureQueriesContext(connection) as ctx:
    Product.objects.filter(name="renamed").delete()
print("delete():", len(ctx.captured_queries), "queries for 1000 rows")
print(Product.objects.count())
```
```text
save() loop: 3 queries
   INSERT INTO "shop_product" ("name", "category_id") VALUES ('loop-0', 1) RETURNING "shop_product"."id"
   INSERT INTO "shop_product" ("name", "category_id") VALUES ('loop-1', 1) RETURNING "shop_product"."id"
   INSERT INTO "shop_product" ("name", "category_id") VALUES ('loop-2', 1) RETURNING "shop_product"."id"
bulk_create 1000 rows: 4 queries
update(): 1000 rows, 1 query
delete(): 15 queries for 1000 rows
3
```

`bulk_create` inserts many objects in few queries (`batch_size` splits large lists). `update()` and `delete()` on a QuerySet run set-based SQL (the `delete()` above needed several statements, because Django first collects the rows that other tables point to, in batches, but nowhere near one per row), but they **skip** each model's `save()` and `delete()` methods and the signals tied to them (section 16), so behaviour that lives there, such as setting a timestamp, does not run. `bulk_update(objs, ["field"])` writes different values to many rows. Always check how many rows a bulk write touched (`update()` returns the count).

### 9.2 `get_or_create` and `update_or_create`

```python run
from shop import *

create_tables(Category, Tag, Product, Supplier, Supply)
t1, created1 = Tag.objects.get_or_create(name="sale")
t2, created2 = Tag.objects.get_or_create(name="sale")
print(t1 == t2, created1, created2)

cat, _ = Category.objects.get_or_create(name="Tools")
p, created = Product.objects.update_or_create(name="Hammer", category=cat, defaults={})
print(p, created)
```
```text
True True False
Hammer True
```

They return `(object, created)`. The part before `defaults` is the **lookup**, `defaults` is only used when creating (or updating, for `update_or_create`). The functions are not magic locks: two requests at the same instant can both see "missing" and both try to create. A `unique=True` column (or `UniqueConstraint`) makes the database reject the loser, and Django then retries the `get`, which is why you should have the unique constraint behind every `get_or_create` lookup.

### 9.3 Transactions: all or nothing

Moving 5 units of stock from product A to product B is two updates. If the process dies after the first one, five units vanish. A **transaction** groups statements so that either all of them happen or none do. In Django, `transaction.atomic()` is the tool:

```python run
from catalog import *
from django.db import transaction

create_tables(Product)
a = Product.objects.create(name="A", sku="A", price="1", quantity=10)
b = Product.objects.create(name="B", sku="B", price="1", quantity=10)


def move_stock(src, dst, units, *, crash=False):
    with transaction.atomic():
        src.quantity -= units
        src.save(update_fields=["quantity"])
        if crash:
            raise RuntimeError("power cut")
        dst.quantity += units
        dst.save(update_fields=["quantity"])


def stock():
    return {p.sku: p.quantity for p in Product.objects.order_by("sku")}

move_stock(a, b, 3)
print("after good move  :", stock())
try:
    move_stock(a, b, 4, crash=True)
except RuntimeError as e:
    print("error:", e)
print("after crashed one:", stock())
```
```text
after good move  : {'A': 7, 'B': 13}
error: power cut
after crashed one: {'A': 7, 'B': 13}
```

The crashed move took 4 units from `A` in the database, then failed, and `atomic()` **rolled back** the first update. Without `atomic()`, SQLite's autocommit would have kept the half-finished state and 4 units would have disappeared. Notes:

- `atomic()` works as a context manager and as a decorator, and can be nested (inner blocks become savepoints).
- `ATOMIC_REQUESTS = True` in `DATABASES` wraps every view in a transaction. It is simple and safe for small sites, at the cost of holding transactions open for the whole request.
- On PostgreSQL and MySQL, `select_for_update()` inside `atomic()` locks the chosen rows until commit, so two requests cannot both read the same stock number and both subtract from it. SQLite has no row locks, so the call does nothing there; the concept is what to learn. Without a lock, use `F()` (section 6.4) to let the database do `quantity = quantity - 5` atomically.
- `transaction.on_commit(func)` runs `func` only after the commit succeeds: the right place to send an email or start a background job, so you never announce something that was rolled back.

### 9.4 Constraints: let the database say no

Validation in forms is not enough: a script, a shell session or a bug can still write bad data. Put the important rules in the database with **constraints**:

```python run
from sandbox import *
from django.db import IntegrityError, transaction

class Item(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="item_price_not_negative"),
            models.UniqueConstraint(fields=["name"], name="item_name_unique"),
        ]

create_tables(Item)
Item.objects.create(name="pen", price="1.00")
for bad in [dict(name="pen", price="2.00"), dict(name="ink", price="-1.00")]:
    try:
        with transaction.atomic():
            Item.objects.create(**bad)
    except IntegrityError as e:
        print("rejected:", bad, "->", e)
print(Item.objects.count())
```
```text
rejected: {'name': 'pen', 'price': '2.00'} -> UNIQUE constraint failed: shop_item.name
rejected: {'name': 'ink', 'price': '-1.00'} -> CHECK constraint failed: item_price_not_negative
1
```

Django 6.1's `CheckConstraint` takes `condition=` (older versions called it `check=`; the old name was removed, so old tutorials fail with a `TypeError`). The `with transaction.atomic()` around each failed insert matters on PostgreSQL: after an `IntegrityError` inside a transaction, you cannot run more queries until you roll back.

Difference to remember: **model validation** (`full_clean()`, forms) gives friendly messages but is only run when someone calls it. **Constraints** are always enforced, with an ugly error. Use both: forms for the user, constraints for the truth.

### 9.5 Reusable queries: custom managers and QuerySets

If `Product.objects.filter(quantity__lte=F("reorder_level"))` appears in five places, give it a name:

```python run
from sandbox import *
from django.db.models import F

class ProductQuerySet(models.QuerySet):
    def low_stock(self):
        return self.filter(quantity__lte=F("reorder_level"))

    def in_stock(self):
        return self.filter(quantity__gt=0)

class Product(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)

    objects = ProductQuerySet.as_manager()

    class Meta:
        app_label = "shop"

    def __str__(self):
        return self.name

create_tables(Product)
for n, q, r in [("pen", 100, 10), ("ink", 3, 5), ("pad", 0, 2), ("clip", 9, 9)]:
    Product.objects.create(name=n, quantity=q, reorder_level=r)

print(Product.objects.low_stock().order_by("name"))
print(Product.objects.low_stock().in_stock().order_by("name"))     # chains, because it is on the QuerySet
```
```text
<ProductQuerySet [<Product: clip>, <Product: ink>, <Product: pad>]>
<ProductQuerySet [<Product: clip>, <Product: ink>]>
```

Putting the methods on a `QuerySet` subclass (and exposing it with `as_manager()`) lets the names chain. We use exactly this for the inventory app in section 18.

### Try it: the lost update

Two staff members open the same product (quantity 10). One sells 3, the other sells 4, both at the same time, with `p.quantity -= n; p.save()`. What ends up in the database, and how do you write it correctly?

<details><summary>Answer</summary>

Both read 10. One writes 7, the other writes 6, and whichever comes last wins: the shop lost 3 or 4 sales. The correct code lets the database do the arithmetic: `Product.objects.filter(pk=pk).update(quantity=F("quantity") - n)`. To also refuse selling more than you have: `.filter(pk=pk, quantity__gte=n).update(...)` and check that it returned `1` (one row changed); `0` means not enough stock. Both are one atomic SQL statement.

</details>


## 10. The admin site

### 10.1 A back office for free

`django.contrib.admin` reads your models and builds a complete interface to list, search, filter, create, edit and delete rows, with login, permissions and a change history. It is meant for **staff** (you, your support team), not for your customers. Many projects get their first usable product from the admin alone, which is the reason the project in this module is called *admin-driven*.

First an account that can log in. `createsuperuser` normally asks questions; for scripts you can pass the values in environment variables:

```bash run
DJANGO_SUPERUSER_PASSWORD="change-me-123" python manage.py createsuperuser --noinput --username admin --email admin@example.com
```
```text
Superuser created successfully.
```

Then register the models. The shortest way is one line per model, `admin.site.register(Product)`. Good admins use a `ModelAdmin` class that says what to show. Here is the admin for the inventory app:

```python
# inventory/admin.py
from decimal import Decimal

from django.contrib import admin, messages
from django.db.models import Count, F

from .models import Category, Product


class ProductInline(admin.TabularInline):
    """Edit a category's products on the category page."""
    model = Product
    extra = 0
    fields = ("name", "sku", "price", "quantity")
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "product_count")
    search_fields = ("name",)
    inlines = [ProductInline]

    def get_queryset(self, request):
        # one query with a GROUP BY, instead of one count() per row
        return super().get_queryset(request).annotate(_products=Count("products"))

    @admin.display(description="Products", ordering="_products")
    def product_count(self, obj):
        return obj._products


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "quantity", "is_low")
    list_filter = ("category",)
    search_fields = ("name", "sku")
    list_editable = ("price",)
    list_select_related = ("category",)
    readonly_fields = ("created",)
    autocomplete_fields = ("category",)
    actions = ["discount_10"]

    @admin.display(description="Low stock?", boolean=True)
    def is_low(self, obj):
        return obj.quantity <= obj.reorder_level

    @admin.action(description="Reduce price by 10 percent")
    def discount_10(self, request, queryset):
        updated = queryset.update(price=F("price") * Decimal("0.9"))
        self.message_user(request, f"{updated} price(s) reduced.", messages.SUCCESS)
```

What each option does:

| Option | Effect |
|---|---|
| `list_display` | columns of the list page; may name fields, methods of the admin, or methods of the model |
| `list_filter` | filter sidebar |
| `search_fields` | the search box (`icontains` on those fields; `^name` means starts-with, `=sku` exact) |
| `list_editable` | edit a column directly in the list |
| `list_select_related` | a `select_related()` for the list page (section 7.4). Django already adds one by itself for a `ForeignKey` named directly in `list_display`; you need this option when a **method** column reaches through the relation |
| `readonly_fields` | show but do not allow editing (also works for computed values) |
| `autocomplete_fields` | a search-as-you-type widget for foreign keys (needs `search_fields` on the related admin) |
| `inlines` | edit child rows on the parent's page |
| `actions` | operations on the selected rows in the list |
| `fieldsets`, `date_hierarchy`, `ordering`, `list_per_page` | layout, date drill-down, default sort, page size |

An action's `description` is passed through Python `%` formatting (it may contain `%(verbose_name_plural)s`), so a literal `%` in it, like "by 10%", crashes the whole list page with `ValueError: incomplete format`. Write "percent", or double it (`%%`).

`@admin.display(description=..., boolean=True, ordering=...)` decorates a method that makes a computed column. Here the computed `is_low` shows a green tick or a red cross.

### 10.2 Using it, tested without a browser

You can start `runserver` and open `/admin/`; here we do the same through the test client, logging in as the superuser. This is also how you test admin pages in real projects.

```python run
from play import client
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext

admin_user = get_user_model().objects.get(username="admin")
client.force_login(admin_user)               # skip the login form in tests

r = client.get("/admin/")
print("index:", r.status_code, "Products" in r.content.decode())

with CaptureQueriesContext(connection) as ctx:
    r = client.get("/admin/inventory/product/")
html = r.content.decode()
print("changelist:", r.status_code, "| rows shown:", html.count('class="field-name"'),
      "| queries:", len(ctx))
print("HDMI cable" in html, "Aux" in html)

r = client.get("/admin/inventory/product/?q=hdmi")
print("search hdmi ->", r.content.decode().count('class="field-name"'), "row")
```
```text
index: 200 True
changelist: 200 | rows shown: 3 | queries: 6
True True
search hdmi -> 1 row
```

Two things in that output are worth reading carefully. The changelist for three products costs a small, fixed number of queries (session, user, count, rows, filter choices); because of `list_select_related`, the category does not add a query per row. And the search box found one product.

Does `list_select_related` matter? Django's list page already joins a `ForeignKey` that you name directly in `list_display` (our `category` column). The danger is a **method** column that reaches through a relation. Let us add one, with and without the option, and count the queries:

```python run
from play import client
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from inventory.admin import ProductAdmin
from inventory.models import Category, Product

admin_user = get_user_model().objects.get(username="admin")
cat = Category.objects.get(name="Cables")
for i in range(7):                                    # more rows -> a bigger difference
    Product.objects.get_or_create(sku=f"X-{i}", defaults=dict(name=f"Extra {i}", category=cat, price="1.00"))


def count_queries(admin_class):
    """Render the list page of an admin class and count the SQL queries."""
    model_admin = admin_class(Product, admin.site)
    request = RequestFactory().get("/admin/inventory/product/")
    request.user = admin_user
    with CaptureQueriesContext(connection) as ctx:
        model_admin.changelist_view(request).render()
    return len(ctx)


class WithMethod(ProductAdmin):
    list_display = ("name", "sku", "category_name")
    list_select_related = ()

    @admin.display(description="Category")
    def category_name(self, obj):
        return obj.category.name               # reaches through the relation


class Fixed(WithMethod):
    list_select_related = ("category",)


print("rows:", Product.objects.count())
print("method column, no list_select_related:  ", count_queries(WithMethod))
print("method column, with list_select_related:", count_queries(Fixed))
```
```text
rows: 10
method column, no list_select_related:   14
method column, with list_select_related: 4
```

That is the N+1 problem inside the admin itself: one extra query per row for the method column, and a flat cost once the option is set. (Here we call the admin class directly with a fake request, which is a handy way to test an admin class.) (After this run the extra rows stay in the example database; it does not matter.)

#### Actions

```python run
from play import client
from django.contrib.auth import get_user_model
from inventory.models import Product

client.force_login(get_user_model().objects.get(username="admin"))
ids = list(Product.objects.filter(sku__in=["CB-USB", "CB-AUX"]).values_list("pk", flat=True))
print("before:", dict(Product.objects.filter(pk__in=ids).values_list("sku", "price")))
r = client.post("/admin/inventory/product/", {"action": "discount_10", "_selected_action": ids})
print("status:", r.status_code, "->", r.headers["Location"])
print("after: ", dict(Product.objects.filter(pk__in=ids).values_list("sku", "price")))
```
```text
before: {'CB-AUX': Decimal('2.00'), 'CB-USB': Decimal('3.50')}
status: 302 -> /admin/inventory/product/
after:  {'CB-AUX': Decimal('1.80'), 'CB-USB': Decimal('3.15')}
```

The action ran `update()` once for the selected rows and flashed a message. Because `update()` skips `save()`, anything in `Product.save()` would be bypassed (section 9.1); for rules that must always hold, prefer constraints.

### 10.3 Who may do what

A user needs `is_staff=True` to enter the admin. What they can do inside is decided by **permissions**: every model automatically gets `add_`, `change_`, `delete_` and `view_` permissions. Superusers have all of them; others get them one by one or through a **group**. Try a staff user who may only *view* products:

```python run
from play import client
from django.contrib.auth.models import Permission, User

u = User.objects.create_user("clerk", password="x-clerk-pass", is_staff=True)
u.user_permissions.add(Permission.objects.get(codename="view_product"))
client.force_login(u)

print("list page:", client.get("/admin/inventory/product/").status_code)
print("add page: ", client.get("/admin/inventory/product/add/").status_code)
print("categories:", client.get("/admin/inventory/category/").status_code)
```
```text
list page: 200
add page:  403
categories: 403
```

`200` for what the clerk may view, `403` for what they may not. Give staff the least permissions they need, and bundle them in groups ("Warehouse", "Managers") rather than per person. For rules like "only the creator may edit", override `has_change_permission(self, request, obj=None)` in the `ModelAdmin`.

### 10.4 Limits of the admin

- It is built for trusted staff. Do not hand it to the public.
- Complex workflows (wizards, special approvals) are better as normal views, with the admin kept for plain data fixes.
- Customise with care: the more you bend it, the more upgrades hurt. Small `ModelAdmin` options go a long way.
- A `list_display` method that touches a relation, or runs a query, causes N+1 (we just measured it).

### Try it: the lazy count

In `CategoryAdmin`, someone writes `def product_count(self, obj): return obj.products.count()` and drops `get_queryset`. The category list has 40 rows. About how many queries does the list page run for the counts, and why is `ordering="_products"` impossible in that version?

<details><summary>Answer</summary>

One `COUNT(*)` per row: about 40 extra queries. And `ordering=` on a column can only name something the database can sort by. A Python method result is not a column, so clicking the column header could not sort. The annotation in `get_queryset` gives the database a real column (`_products`) to sort and to compute in one `GROUP BY` query.

</details>

## 11. Forms and ModelForms

### 11.1 A plain form: validate before you trust

Anything that comes from a user is untrusted text. A Django **form** declares the fields, runs the checks and gives you clean Python values. You can use a form without a database or HTML:

```python run
import django
from django.conf import settings
settings.configure()
django.setup()

from django import forms

class RestockForm(forms.Form):
    sku = forms.CharField(max_length=20)
    units = forms.IntegerField(min_value=1, max_value=500)
    note = forms.CharField(required=False)

    def clean_sku(self):                       # clean_<field>: one field
        return self.cleaned_data["sku"].strip().upper()

    def clean(self):                           # clean(): rules that involve several fields
        data = super().clean()
        if data.get("units") and data["units"] > 100 and not data.get("note"):
            self.add_error("note", "Orders over 100 units need a note.")
        return data

good = RestockForm({"sku": " cb-usb ", "units": "25"})
print(good.is_valid(), good.cleaned_data)

bad = RestockForm({"sku": "", "units": "abc"})
print(bad.is_valid())
print(bad.errors.get_json_data())

big = RestockForm({"sku": "x", "units": "300"})
print(big.is_valid(), dict(big.errors))
```
```text
True {'sku': 'CB-USB', 'units': 25, 'note': ''}
False
{'sku': [{'message': 'This field is required.', 'code': 'required'}], 'units': [{'message': 'Enter a whole number.', 'code': 'invalid'}]}
False {'note': ['Orders over 100 units need a note.']}
```

Study what happened:

- Form input is always **strings**. `IntegerField` converted `"25"` into the integer `25` in `cleaned_data`. Use `cleaned_data`, never the raw input.
- `is_valid()` runs all validation; afterwards `form.errors` maps each field to its messages. `non_field_errors` hold problems from `clean()` that are not tied to one field.
- `clean_<field>()` cleans one field and must **return** the value (forgetting `return` makes the field `None`: the same trap as Pydantic validators in swe.05). `clean()` checks combinations.

The three levels of checking, from cheap to strict: **field options** (`max_length`, `min_value`, `required`), **validators and clean methods**, and **database constraints** (section 9.4). A form is the friendly front door; constraints are the lock.

### 11.2 ModelForm: a form built from a model

Most forms edit a model, and repeating the fields would be a chore. A `ModelForm` builds the fields from the model and adds `.save()`:

```python
# inventory/forms.py
from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "category", "price", "quantity", "reorder_level"]   # list them, always

    def clean_sku(self):
        return self.cleaned_data["sku"].strip().upper()

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Price must be above zero.")
        return price
```

Two warnings about `Meta.fields`:

- `fields = "__all__"` or `exclude = [...]` are tempting but **dangerous**: add a field to the model later (say `is_staff` on a user form, or `cost_price`) and it silently becomes editable by every visitor. This is called **mass assignment**. List the fields you allow.
- Uniqueness (`sku`) is checked by the form for you: it knows the model field has `unique=True`, and reports a friendly error before the database does.

```python run
from play import client
from inventory.forms import ProductForm
from inventory.models import Category

cables = Category.objects.get(name="Cables")
f = ProductForm({"name": "Splitter", "sku": " cb-spl ", "category": cables.pk, "price": "-2", "quantity": "3", "reorder_level": "5"})
print(f.is_valid(), dict(f.errors))

f = ProductForm({"name": "Splitter", "sku": " cb-spl ", "category": cables.pk, "price": "4.25", "quantity": "3", "reorder_level": "5"})
print(f.is_valid())
obj = f.save()
print(obj, obj.pk, obj.price)

dup = ProductForm({"name": "Another", "sku": "CB-SPL", "category": cables.pk, "price": "1", "quantity": "1", "reorder_level": "1"})
print(dup.is_valid(), dict(dup.errors))
```
```text
False {'price': ['Price must be above zero.']}
True
Splitter (CB-SPL) 11 4.25
False {'sku': ['Product with this SKU already exists.']}
```

`form.save()` creates the row (or updates it if you passed `instance=`). `form.save(commit=False)` returns the unsaved object so you can fill fields the form does not ask for (the logged-in user, a timestamp) and then call `obj.save()` yourself. For many-to-many fields after `commit=False`, call `form.save_m2m()`.

### 11.3 Using a form in a view: show, validate, redirect

A page with a form follows one pattern:

1. `GET`: show an empty (or pre-filled) form.
2. `POST`: build the form from `request.POST`. If valid: save, then **redirect** to another page. If invalid: show the **same form with its errors**.

The redirect after a successful POST is called **Post/Redirect/Get**. Without it, pressing the browser's reload button re-sends the POST and creates a duplicate row.

We now also make the views use the database instead of the fake dictionary:

```python
# inventory/views.py
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product


def home(request):
    return HttpResponse("Inventory home")


def product_list(request):
    products = Product.objects.select_related("category")
    return render(request, "inventory/product_list.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return JsonResponse({"id": product.pk, "name": product.name, "sku": product.sku,
                         "price": str(product.price), "quantity": product.quantity})


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            return redirect("inventory:product-detail", product_id=product.pk)
    else:
        form = ProductForm()
    return render(request, "inventory/product_form.html", {"form": form})
```

```html
<!-- inventory/templates/inventory/product_form.html -->
{% extends "inventory/base.html" %}

{% block title %}New product{% endblock %}

{% block content %}
<h1>New product</h1>
<form method="post">
  {% csrf_token %}
  {{ form.as_div }}
  <button type="submit">Save</button>
</form>
{% endblock %}
```

The product list template from section 5 used `p.id`; with real model objects we use `p.pk` and show the category. Replace it, and add the URL:

```html
<!-- inventory/templates/inventory/product_list.html -->
{% extends "inventory/base.html" %}

{% block title %}Products{% endblock %}

{% block content %}
<h1>Products</h1>
<p><a href="{% url 'inventory:product-create' %}">Add a product</a></p>
<ul>
{% for p in products %}
  <li><a href="{% url 'inventory:product-detail' product_id=p.pk %}">{{ p.name }}</a> ({{ p.category }}): {{ p.quantity }} in stock</li>
{% empty %}
  <li>No products yet.</li>
{% endfor %}
</ul>
{% endblock %}
```

```python
# inventory/urls.py
from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product-list"),
    path("products/new/", views.product_create, name="product-create"),
    path("products/<int:product_id>/", views.product_detail, name="product-detail"),
]
```

Order matters: `products/new/` is listed before `products/<int:...>/`. Here `int` would not match `new` anyway, but with a `<str:...>` converter the order would decide which view answers.

```python run
from play import client
from inventory.models import Product

r = client.get("/products/new/")
print(r.status_code, "csrfmiddlewaretoken" in r.content.decode())

good = {"name": "Splitter 2", "sku": "cb-sp2", "category": 1, "price": "4.25", "quantity": 3, "reorder_level": 5}
r = client.post("/products/new/", good)
print("valid POST   ->", r.status_code, r.headers["Location"])

r = client.post("/products/new/", {**good, "sku": "cb-sp3", "price": "0"})
print("invalid POST ->", r.status_code, "| error shown:", "Price must be above zero." in r.content.decode())
print(Product.objects.filter(sku__startswith="CB-SP").count(), "splitters saved")

strict = __import__("django.test", fromlist=["Client"]).Client(enforce_csrf_checks=True)
r = strict.post("/products/new/", good)
print("no CSRF token ->", r.status_code)
```
```text
200 True
valid POST   -> 302 /products/12/
invalid POST -> 200 | error shown: True
2 splitters saved
no CSRF token -> 403
```

An invalid form is answered with `200` and the page redisplayed with the messages, which is the normal HTML form behaviour (the status code only becomes `4xx` for APIs). The last two lines show **CSRF**: the test client skips the check by default, so we turned it on. Without the hidden token that `{% csrf_token %}` writes into the form, a POST from another site (using the visitor's logged-in cookie) is refused with `403`. Never disable `CsrfViewMiddleware` to "make a form work"; add the tag.

> **CSRF and JSON clients.** The token is for browser forms. API clients that send a token in a header (DRF with `TokenAuthentication` or JWT) are not vulnerable in the same way, because the browser does not attach the header by itself. DRF's `SessionAuthentication` does enforce CSRF (section 15).

### Try it: mass assignment

A teammate writes `class UserForm(ModelForm): class Meta: model = User; exclude = ["password"]` for the "edit my profile" page. What goes wrong?

<details><summary>Answer</summary>

`exclude` lists what is *removed*, so every other field is editable, including `is_staff`, `is_superuser` and `groups`. A visitor who adds `is_superuser=on` to the POST data makes themselves an administrator. This is the mass-assignment bug. Fix: `fields = ["first_name", "last_name", "email"]`, an explicit allow-list.

</details>


## 12. Generic class-based views

### 12.1 CRUD in a few lines

Almost every site has the same five screens per model: a **list**, a **detail** page, a **create** form, an **update** form and a **delete** confirmation. Django's generic class-based views implement them. You say *which model* and *which template*; they do the rest (fetch, validate, save, redirect).

| Class | Screen | Default template | Needs |
|---|---|---|---|
| `ListView` | list | `<app>/<model>_list.html` | `model` or `queryset` |
| `DetailView` | one object | `<app>/<model>_detail.html` | `pk` or `slug` in the URL |
| `CreateView` | new form | `<app>/<model>_form.html` | `fields` or `form_class` |
| `UpdateView` | edit form | `<app>/<model>_form.html` | same, plus `pk` |
| `DeleteView` | confirm and delete | `<app>/<model>_confirm_delete.html` | `success_url` |

Now rewrite the inventory views (the function views of section 11 become classes):

```python
# inventory/views.py
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


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("inventory:product-list")
```

```python
# inventory/urls.py
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
```

The generic create and update views need to know where to go after a successful save. If the model defines `get_absolute_url()`, they use it. Add it to `Product` (a method change needs no migration):

```python
# inventory/models.py
from django.db import models
from django.db.models import F
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def low_stock(self):
        return self.filter(quantity__lte=F("reorder_level"))


class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField("SKU", max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse("inventory:product-detail", kwargs={"pk": self.pk})

    @property
    def is_low(self):
        return self.quantity <= self.reorder_level
```

```bash run
python manage.py makemigrations --check --dry-run
```
```text
No changes detected
```

Adding a method, a property or a custom manager does not change the table, so no migration is needed.

The templates. The list template has a search box and page links; the detail and delete templates are short:

```html
<!-- inventory/templates/inventory/product_list.html -->
{% extends "inventory/base.html" %}

{% block title %}Products{% endblock %}

{% block content %}
<h1>Products</h1>
<form method="get"><input name="q" value="{{ q }}" placeholder="Search name or SKU"> <button>Search</button></form>
<p><a href="{% url 'inventory:product-create' %}">Add a product</a></p>
<ul>
{% for p in products %}
  <li><a href="{{ p.get_absolute_url }}">{{ p.name }}</a> ({{ p.category }}): {{ p.quantity }} in stock{% if p.is_low %} <strong>LOW</strong>{% endif %}</li>
{% empty %}
  <li>No products found.</li>
{% endfor %}
</ul>
{% if is_paginated %}
<p>Page {{ page_obj.number }} of {{ paginator.num_pages }}
{% if page_obj.has_previous %}<a href="?page={{ page_obj.previous_page_number }}&q={{ q|urlencode }}">previous</a>{% endif %}
{% if page_obj.has_next %}<a href="?page={{ page_obj.next_page_number }}&q={{ q|urlencode }}">next</a>{% endif %}
</p>
{% endif %}
{% endblock %}
```

```html
<!-- inventory/templates/inventory/product_detail.html -->
{% extends "inventory/base.html" %}

{% block title %}{{ product.name }}{% endblock %}

{% block content %}
<h1>{{ product.name }}</h1>
<p>SKU {{ product.sku }} | {{ product.category }} | {{ product.price }} | {{ product.quantity }} in stock</p>
<p><a href="{% url 'inventory:product-update' pk=product.pk %}">Edit</a>
 <a href="{% url 'inventory:product-delete' pk=product.pk %}">Delete</a></p>
{% endblock %}
```

```html
<!-- inventory/templates/inventory/product_confirm_delete.html -->
{% extends "inventory/base.html" %}

{% block content %}
<h1>Delete {{ product.name }}?</h1>
<form method="post">
  {% csrf_token %}
  <button type="submit">Yes, delete it</button>
  <a href="{{ product.get_absolute_url }}">Cancel</a>
</form>
{% endblock %}
```

Look at what Django chose for names: the object is available as `product` (from the model name) in detail and delete templates, and the list as `object_list` plus the `products` name we set with `context_object_name`. The `product_form.html` from section 11 serves both create and update. Try the five screens:

```python run
from play import client
from inventory.models import Product

r = client.get("/products/")
html = r.content.decode()
print("list:", r.status_code, "| items on page 1:", html.count("<li>"), "| paginated:", "Page 1 of" in html)
print("page 2:", client.get("/products/?page=2").status_code, "| page 99:", client.get("/products/?page=99").status_code)
print("search 'cable':", client.get("/products/?q=cable").content.decode().count("<li>"), "item(s)")

p = Product.objects.get(sku="CB-USB")
print("detail:", client.get(p.get_absolute_url()).status_code)

r = client.post(f"/products/{p.pk}/edit/", {"name": "USB cable 2m", "sku": "CB-USB", "category": p.category_id,
                                            "price": "3.20", "quantity": 120, "reorder_level": 20})
print("edit  :", r.status_code, "->", r.headers["Location"])
p.refresh_from_db()
print("now   :", p.name, p.price)

r = client.post("/products/new/", {"name": "Tmp", "sku": "TMP-1", "category": p.category_id, "price": "1", "quantity": 1, "reorder_level": 1})
tmp_url = r.headers["Location"]
print("create:", r.status_code, "->", tmp_url)
print("delete page:", client.get(tmp_url + "delete/").status_code)
r = client.post(tmp_url + "delete/")
print("delete:", r.status_code, "->", r.headers["Location"], "| left:", Product.objects.filter(sku="TMP-1").count())
```
```text
list: 200 | items on page 1: 5 | paginated: True
page 2: 200 | page 99: 404
search 'cable': 3 item(s)
detail: 200
edit  : 302 -> /products/2/
now   : USB cable 2m 3.20
create: 302 -> /products/13/
delete page: 200
delete: 302 -> /products/ | left: 0
Not Found: /products/
```

### 12.2 When to use generic views, and when not

Use them for standard screens: they are short, tested by thousands of projects and easy to read for other Django developers. Customise through small hooks rather than rewriting:

| Hook | Use it to... |
|---|---|
| `get_queryset()` | filter, search, restrict to the current user |
| `get_context_data()` | add values for the template |
| `form_valid(form)` | do extra work when the form is valid (set the owner, send a message) |
| `get_success_url()` | choose where to go next |
| `get_form_kwargs()` | pass extra data into the form |
| `dispatch()` | run code before any method (permission checks) |

Use a plain function view when the screen does not fit the CRUD mould (a dashboard, a multi-step process). Do not stretch a generic view until it is harder to read than a function. **Mixins** add behaviour (`LoginRequiredMixin` in the next section); they go on the **left** of the base view in the class line.

### Try it: where is the 404?

A user opens `/products/99999/edit/`. Which line of which class raises the 404, and what do you write to show them a custom page?

<details><summary>Answer</summary>

`UpdateView.get_object()` calls `get_object_or_404(queryset, pk=...)`, which raises `Http404`. Django then renders the `404.html` template if the project has one in its templates folder (with `DEBUG = False`; with `DEBUG = True` you see the technical 404). A project-wide `templates/404.html` is all you need.

</details>

## 13. Authentication and permissions

### 13.1 Authentication versus authorisation

**Authentication** answers "who are you?" **Authorisation** answers "what may you do?" Django has both built in (`django.contrib.auth`): a `User` model, password hashing, login and logout views, sessions, **permissions** and **groups**. The deep security topics (OAuth, JWT, threat models) belong to swe.07. This section is the Django-specific toolkit.

### 13.2 Users and passwords

```python run
import django
from django.conf import settings
settings.configure(
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
    SECRET_KEY="demo-only-key-000000000000000000000000000000000000",
)
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.management import call_command

call_command("migrate", verbosity=0)

u = User.objects.create_user("ada", email="ada@example.com", password="correct horse battery")
print("stored:", u.password.split("$")[0], "| length", len(u.password))
print("plain text anywhere?", "correct horse" in u.password)
print(u.check_password("correct horse battery"), u.check_password("wrong"))
print("authenticate ok  :", authenticate(username="ada", password="correct horse battery"))
print("authenticate bad :", authenticate(username="ada", password="nope"))

u.set_password("new password 123")
u.save()
print(u.check_password("new password 123"))
print("is_staff / is_superuser / is_active:", u.is_staff, u.is_superuser, u.is_active)
```
```text
stored: pbkdf2_sha256 | length 89
plain text anywhere? False
True False
authenticate ok  : ada
authenticate bad : None
True
is_staff / is_superuser / is_active: False False True
```

Never store or compare passwords yourself. `create_user` and `set_password` hash the password with a slow, salted algorithm (`pbkdf2_sha256` by default; the stored string holds the algorithm, iteration count, salt and hash, so Django can upgrade old hashes). `authenticate()` returns the user or `None`. Direct `User.objects.create(password="x")` stores the text **unhashed**, a classic bug: use `create_user`.

### 13.3 Login, logout and sessions

HTTP is stateless, so after a successful login Django stores the user's id in a **session** (a row in the `django_session` table by default) and gives the browser a cookie, `sessionid`, containing only a random key. On later requests the `SessionMiddleware` and `AuthenticationMiddleware` turn that cookie into `request.user`. Add Django's login and logout views to the project:

```python
# inventory_site/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("inventory.urls")),
]
```

```html
<!-- inventory/templates/registration/login.html -->
{% extends "inventory/base.html" %}

{% block title %}Log in{% endblock %}

{% block content %}
<h1>Log in</h1>
<form method="post">
  {% csrf_token %}
  {{ form.as_div }}
  <input type="hidden" name="next" value="{{ next }}">
  <button type="submit">Log in</button>
</form>
{% endblock %}
```



```bash run
cat >> inventory_site/settings.py <<'SETTINGS'

LOGIN_REDIRECT_URL = "inventory:product-list"
LOGOUT_REDIRECT_URL = "inventory:home"
SETTINGS
tail -4 inventory_site/settings.py
python manage.py shell --no-imports -c "from django.urls import reverse; print(reverse('login'), reverse('logout'), reverse('password_change'))"
```
```text
}

LOGIN_REDIRECT_URL = "inventory:product-list"
LOGOUT_REDIRECT_URL = "inventory:home"
/accounts/login/ /accounts/logout/ /accounts/password_change/
```

`django.contrib.auth.urls` gives `login/`, `logout/` and the password change and reset pages, with the names `login`, `logout`, and so on. In Django 6.x logout must be a **POST** (a plain link would let any web page log you out by loading an image). Let us log in through the real view:

```python run
from play import client
from django.contrib.auth.models import User

User.objects.create_user("sam", password="warehouse-pass-1")

r = client.post("/accounts/login/", {"username": "sam", "password": "wrong"})
print("bad password :", r.status_code, "| error shown:", "Please enter a correct username and password" in r.content.decode())
r = client.post("/accounts/login/", {"username": "sam", "password": "warehouse-pass-1"})
print("good password:", r.status_code, "->", r.headers["Location"])
print("session cookie set:", "sessionid" in client.cookies)
r = client.post("/accounts/logout/")
print("logout:", r.status_code, "->", r.headers["Location"], "| cookie value now:", repr(client.cookies["sessionid"].value))
```
```text
bad password : 200 | error shown: True
good password: 302 -> /products/
session cookie set: True
logout: 302 -> / | cookie value now: ''
```

### 13.4 Protecting views

Make the create, update and delete screens require a **permission** with `PermissionRequiredMixin` (which includes the login check). Rewrite the views file:

```python
# inventory/views.py
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
```

`PermissionRequiredMixin` handles two cases differently: **anonymous** users are redirected to the login page, and **logged-in users without the permission** get `403 Forbidden`. Use `LoginRequiredMixin` alone when any logged-in user may enter. For function views the same ideas are decorators: `@login_required` and `@permission_required("inventory.add_product", raise_exception=True)`.

```python run
import play                      # prepares Django
from django.contrib.auth.models import Group, Permission, User
from django.test import Client

# a group with the right permissions: this is how you manage staff in practice
warehouse, _ = Group.objects.get_or_create(name="Warehouse")
warehouse.permissions.set(Permission.objects.filter(codename__in=["add_product", "change_product"]))

sam = User.objects.get(username="sam")
sam.groups.add(warehouse)
nobody = User.objects.create_user("guest", password="guest-pass-123")

anon = Client()
r = anon.get("/products/new/")
print("anonymous      :", r.status_code, "->", r.headers["Location"])

c = Client(); c.force_login(nobody)
print("no permission  :", c.get("/products/new/").status_code)

c = Client(); c.force_login(sam)
print("Warehouse group:", c.get("/products/new/").status_code, "(add)", c.get("/products/1/edit/").status_code, "(edit)",
      c.get("/products/1/delete/").status_code, "(delete)")
```
```text
anonymous      : 302 -> /accounts/login/?next=/products/new/
no permission  : 403
Warehouse group: 200 (add) 200 (edit) 403 (delete)
```

Group membership gave Sam `add` and `change` but not `delete`. Two details: `force_login` (for tests) skips the password check, and a user object caches its permissions after the first `has_perm` call, so reload the user after changing permissions.

Roles and permissions are broad ("may delete any product"). The next level is **object ownership**: "may edit *my own* orders". Django does not enforce this for you. You do it in `get_queryset()`, so other people's objects simply do not exist for the current user:

```python
class MyOrderListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user)      # 404 for other people's ids
```

A user who guesses another user's id gets a 404, not the data and not even a hint that the object exists. Forgetting this filter is the classic **insecure direct object reference** (IDOR) bug, and swe.07 returns to it.

### 13.5 The custom user model decision

Django's `User` has username, email, names and flags. If you may ever need more (a phone number, a company, login by email), define your own **before the first migration** of the project, even if it is empty:

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

# settings.py
AUTH_USER_MODEL = "accounts.User"
```

Changing `AUTH_USER_MODEL` after tables exist is one of the most painful migrations in Django. Always refer to it with `get_user_model()` or `settings.AUTH_USER_MODEL`, never by importing `django.contrib.auth.models.User` in project code. (This chapter's inventory project uses the default `User` to stay small; a real one should not.)

### Try it: 403 or redirect?

A logged-in user without permission opens `/products/new/` in a browser. Which status code do they get? What changes if they are anonymous? And which mixin would you use on a page that only needs *any* logged-in user?

<details><summary>Answer</summary>

The logged-in user without the permission gets **403**. The anonymous user is **redirected (302)** to the login page with `?next=/products/new/`, so that after logging in they come back. For "any logged-in user", use `LoginRequiredMixin`.

</details>

## 14. Testing Django projects

### 14.1 `TestCase` and the test database

Django's test runner builds a **separate, empty test database** for each run, so tests never touch your real data. `django.test.TestCase` wraps each test in a transaction that is rolled back at the end, which makes tests fast and independent. The test **client** (`self.client`) calls your views in-process, with cookies, sessions and redirects. Tests live in `tests.py` or in a `tests/` package, in classes with methods named `test_*`.

First tests for the inventory app:

```python
# inventory/tests.py
from decimal import Decimal

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .forms import ProductForm
from .models import Category, Product


class ProductModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # runs once for the class; data is shared (and protected from changes) between tests
        cls.cables = Category.objects.create(name="Cables")

    def test_low_stock_uses_reorder_level(self):
        Product.objects.create(name="A", sku="A", category=self.cables, price="1", quantity=2, reorder_level=5)
        Product.objects.create(name="B", sku="B", category=self.cables, price="1", quantity=50, reorder_level=5)
        self.assertEqual([p.sku for p in Product.objects.low_stock()], ["A"])

    def test_is_low_is_inclusive(self):
        p = Product(quantity=5, reorder_level=5)
        self.assertTrue(p.is_low, "quantity == reorder_level should count as low")

    def test_price_must_be_positive_in_the_form(self):
        form = ProductForm({"name": "x", "sku": "x", "category": self.cables.pk, "price": "0", "quantity": 1, "reorder_level": 1})
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)


class ProductViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="Tools")
        for i in range(12):
            Product.objects.create(name=f"Tool {i:02}", sku=f"T-{i:02}", category=cls.cat, price="2.50", quantity=i)
        cls.clerk = User.objects.create_user("clerk", password="pw-clerk-123")
        cls.clerk.user_permissions.add(Permission.objects.get(codename="add_product"))

    def test_list_is_paginated(self):
        r = self.client.get(reverse("inventory:product-list"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context["products"]), 5)
        self.assertContains(r, "Page 1 of 3")

    def test_list_costs_two_queries_whatever_the_size(self):
        # one COUNT for the paginator, one SELECT with the category joined
        with self.assertNumQueries(2):
            self.client.get(reverse("inventory:product-list"))

    def test_search(self):
        r = self.client.get(reverse("inventory:product-list"), {"q": "tool 03"})
        self.assertEqual([p.sku for p in r.context["products"]], ["T-03"])

    def test_anonymous_cannot_create(self):
        url = reverse("inventory:product-create")
        r = self.client.get(url)
        self.assertRedirects(r, f"/accounts/login/?next={url}")

    def test_user_without_permission_gets_403(self):
        self.client.force_login(User.objects.create_user("nope", password="pw-nope-123"))
        self.assertEqual(self.client.get(reverse("inventory:product-create")).status_code, 403)

    def test_clerk_can_create(self):
        self.client.force_login(self.clerk)
        data = {"name": "Plane", "sku": "pl-1", "category": self.cat.pk, "price": "19.90", "quantity": 4, "reorder_level": 2}
        r = self.client.post(reverse("inventory:product-create"), data)
        plane = Product.objects.get(sku="PL-1")                  # the form upper-cased it
        self.assertRedirects(r, plane.get_absolute_url())
        self.assertEqual(plane.price, Decimal("19.90"))
```

Handy assertions: `assertContains(response, text)`, `assertRedirects(response, url)`, `assertEqual(response.status_code, 200)`, `assertTemplateUsed`, `assertNumQueries(n)`, `assertFormError`. `response.context` gives the template variables. `setUpTestData` is faster than `setUp` because the data is created once per class.

Run the whole suite. `manage.py test` finds every `test*.py` file:

```bash run
python manage.py test
```
```text
Found 9 test(s).
System check identified no issues (0 silenced).
Creating test database for alias 'default'...
.........
----------------------------------------------------------------------
Ran 9 tests in 1.146s

OK
Destroying test database for alias 'default'...
```

(The time in the output depends on your machine.) Useful flags: `python manage.py test inventory.tests.ProductViewTests.test_search` runs one test; `-k search` selects by name; `--parallel` uses several processes; `--failfast` stops at the first failure; `--keepdb` reuses the test database between runs; `-v 2` lists every test and migration.

### 14.2 What a failure looks like

When a test fails, read the message from the bottom: the assertion first, then the line. Here is a deliberate mistake, where we claim the list page needs one query when it needs two (a COUNT for the paginator and the SELECT):

```bash run
cat > inventory/test_demo_fail.py <<'DEMO'
from django.test import TestCase
from django.urls import reverse

from inventory.models import Category, Product


class Demo(TestCase):
    def test_wrong_claim(self):
        cat = Category.objects.create(name="C")
        Product.objects.create(name="P", sku="P", category=cat, price="1")
        with self.assertNumQueries(1):
            self.client.get(reverse("inventory:product-list"))
DEMO
python manage.py test inventory.test_demo_fail 2>&1 | grep -v "^$" | head -30
rm inventory/test_demo_fail.py
```
```text
Creating test database for alias 'default'...
F
======================================================================
FAIL: test_wrong_claim (inventory.test_demo_fail.Demo.test_wrong_claim)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/you/inventory_site/inventory/test_demo_fail.py", line 11, in test_wrong_claim
    with self.assertNumQueries(1):
         ~~~~~~~~~~~~~~~~~~~~~^^^
AssertionError: 2 != 1 : 2 queries executed, 1 expected
Captured queries were:
1. SELECT COUNT(*) AS "__count" FROM "inventory_product"
2. SELECT "inventory_product"."id", "inventory_product"."name", "inventory_product"."sku", "inventory_product"."category_id", "inventory_product"."price", "inventory_product"."quantity", "inventory_product"."reorder_level", "inventory_product"."created", "inventory_category"."id", "inventory_category"."name" FROM "inventory_product" INNER JOIN "inventory_category" ON ("inventory_product"."category_id" = "inventory_category"."id") ORDER BY "inventory_product"."name" ASC LIMIT 1
----------------------------------------------------------------------
Ran 1 test in 0.020s
FAILED (failures=1)
Destroying test database for alias 'default'...
Found 1 test(s).
System check identified no issues (0 silenced).
```

Django prints the queries that actually ran, which is what you need to decide whether the test or the code is wrong.

### 14.3 What to test

- **Models and managers:** your custom QuerySet methods and properties (`low_stock`, `is_low`), and constraints (an `IntegrityError` for bad data).
- **Forms:** valid and invalid data, one test per rule.
- **Views:** status codes, redirects, who may do what (anonymous, user, staff), the content, and **how many queries**.
- **Business rules:** stock never goes negative, an order total equals the sum of its lines (section 18).

Do not test Django itself ("does `CharField` store a string?"); test your rules. Keep each test independent of the others, and build only the data that test needs. For many objects, a factory library (`factory_boy`) or small helper functions beat copy-pasted `create()` lines. `pytest` with the `pytest-django` plugin is a popular alternative runner with plain `assert` statements; the client and the test database work the same way.

### Try it: which test catches the IDOR?

Write down (do not code) a test that would have caught the missing `owner=request.user` filter of section 13.4.

<details><summary>Answer</summary>

Create two users, A and B, and an order owned by A. Log in as B, request A's order by its id, and assert that the status code is `404` (and that the page does not contain A's data). Also request the list page as B and assert that A's order is not in `response.context["object_list"]`. The lesson: a security rule needs a test with two actors, because with only one actor the bug is invisible.

</details>


## 15. Django REST Framework basics

### 15.1 What DRF adds

Plain Django can return `JsonResponse`, but you would write the parsing, validation, error format, pagination, authentication and docs yourself. **Django REST Framework (DRF)** is the standard library on top of Django for building APIs. Its pieces map to ideas you know from FastAPI:

| DRF piece | Job | FastAPI equivalent |
|---|---|---|
| **Serializer** | validate input, convert objects to/from JSON | Pydantic model |
| **Request / Response** | parsed data in `request.data`; content negotiation | the typed endpoint arguments |
| **APIView / generic views / ViewSet** | the handlers | path operation functions |
| **Router** | builds the URL set for a ViewSet | `APIRouter` |
| **Authentication / permission classes** | who are you, may you | `Depends(...)` |
| **Pagination, filter backends** | list handling | query parameters you write |
| **Browsable API** | HTML page to try the API | `/docs` |

DRF is not part of Django; it is a separate installed app (`rest_framework`). We keep the same inventory project and add an API next to the HTML pages. Register the app and set project-wide defaults in `settings.py`:

```bash run
sed -i "s/    'inventory',/    'rest_framework',\n    'inventory',/" inventory_site/settings.py
cat >> inventory_site/settings.py <<'SETTINGS'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
}
SETTINGS
python manage.py check
```
```text
System check identified no issues (0 silenced).
```

### 15.2 Serializers: validation and conversion

A serializer plays the same role a form played for HTML: it validates input and produces clean values. You can try one with no project:

```python run
import django
from django.conf import settings
settings.configure()
django.setup()

from rest_framework import serializers

class RestockSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=20)
    units = serializers.IntegerField(min_value=1, max_value=500)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_sku(self, value):                  # validate_<field>: like clean_<field>
        return value.strip().upper()

    def validate(self, attrs):                      # whole-object rules
        if attrs["units"] > 100 and not attrs.get("note"):
            raise serializers.ValidationError({"note": "Orders over 100 units need a note."})
        return attrs

s = RestockSerializer(data={"sku": " cb-usb ", "units": "25"})
print(s.is_valid(), dict(s.validated_data))

s = RestockSerializer(data={"sku": "", "units": 0})
print(s.is_valid(), s.errors)

s = RestockSerializer(data={"sku": "x", "units": 300})
print(s.is_valid(), s.errors)

out = RestockSerializer({"sku": "KB-1", "units": 5})         # the other direction: object -> primitives
print(out.data)
```
```text
True {'sku': 'CB-USB', 'units': 25}
False {'sku': [ErrorDetail(string='This field may not be blank.', code='blank')], 'units': [ErrorDetail(string='Ensure this value is greater than or equal to 1.', code='min_value')]}
False {'note': [ErrorDetail(string='Orders over 100 units need a note.', code='invalid')]}
{'sku': 'KB-1', 'units': 5}
```

The error dictionary has the same shape you will see in a `400` response: field name → list of messages. Compare with FastAPI's `422` body (swe.05): DRF's is simpler and keyed by field.

A **`ModelSerializer`** builds the fields from a model, as `ModelForm` does:

```python
# inventory/serializers.py
from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_low = serializers.BooleanField(read_only=True)
    sku = serializers.CharField(max_length=20, validators=[])      # uniqueness is checked by hand below

    class Meta:
        model = Product
        fields = ["id", "name", "sku", "category", "category_name", "price", "quantity", "reorder_level", "is_low"]
        read_only_fields = ["quantity"]            # quantity changes only through stock movements

    def validate_sku(self, value):
        value = value.strip().upper()
        others = Product.objects.filter(sku=value)
        if self.instance is not None:
            others = others.exclude(pk=self.instance.pk)
        if others.exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be above zero.")
        return value

```

Notes on the code:

- `fields` is an **explicit list**, for the same mass-assignment reasons as `ModelForm` (section 11.2). `read_only_fields` keeps clients from writing the stock count.
- `category_name` uses `source="category.name"`, which walks a relation per object. That is an N+1 trap unless the view uses `select_related("category")`, as we do below.
- `sku` is declared by hand with `validators=[]` on purpose. A `ModelSerializer` adds a `UniqueValidator` for a `unique=True` column, and it runs on the **raw** value, **before** `validate_sku` upper-cases it. Then `"gd-1"` passes the check, `validate_sku` turns it into `"GD-1"`, and the database raises `IntegrityError` (a 500 error) for an existing `GD-1`. Our version normalises first and then checks. A `ModelForm` does not have this problem, because it runs `clean_sku` before the model's uniqueness check. The database constraint stays as the last line of defence.
- Numbers like `price` are serialized as **strings** (`"19.90"`) by default, so no precision is lost on the way to JavaScript.

### 15.3 Views: three levels

| Level | Code | Use when |
|---|---|---|
| `APIView` | write `get()`, `post()` yourself | an unusual endpoint |
| generic views (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`, ...) | set `queryset` and `serializer_class` | one URL pair per model |
| **`ModelViewSet`** + router | one class for list, create, retrieve, update, partial update, destroy | standard CRUD for a model, the DRF default |

The generated URLs of a `ModelViewSet` registered as `products`: `GET/POST /products/` and `GET/PUT/PATCH/DELETE /products/{id}/`. Extra endpoints are added with `@action`.

The pieces of a viewset are small; we write the real one in 15.4.

### 15.4 The inventory API, step by step

`ProductViewSet` is the whole CRUD API for products; the router creates the URLs. The test client for APIs is `APIClient`.

```python
# inventory/api.py
from rest_framework import filters, viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.routers import DefaultRouter

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]    # reuse add/change/delete permissions
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "sku"]                                 # ?search=usb
    ordering_fields = ["name", "price", "quantity"]                 # ?ordering=-price


router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
```

```python
# inventory_site/urls.py
from django.contrib import admin
from django.urls import include, path

from inventory.api import router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", include(router.urls)),
    path("", include("inventory.urls")),
]
```

```python run
import json

import play
from django.contrib.auth.models import Permission, User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

api = APIClient()

with CaptureQueriesContext(connection) as ctx:
    r = api.get("/api/products/")
print(r.status_code, r["Content-Type"])
body = r.json()
print(sorted(body), "| count:", body["count"], "| next:", body["next"], "| results on page:", len(body["results"]))
print(json.dumps(body["results"][0]))
print("queries for the page:", len(ctx))

print("search:", [p["sku"] for p in api.get("/api/products/", {"search": "usb"}).json()["results"]])
print("order :", [p["price"] for p in api.get("/api/products/", {"ordering": "-price"}).json()["results"]])
print("page 2:", api.get("/api/products/?page=2").json()["previous"])
```
```text
200 application/json
['count', 'next', 'previous', 'results'] | count: 12 | next: http://testserver/api/products/?page=2 | results on page: 5
{"id": 3, "name": "Aux cable", "sku": "CB-AUX", "category": 1, "category_name": "Cables", "price": "1.80", "quantity": 4, "reorder_level": 5, "is_low": true}
queries for the page: 2
search: ['CB-USB']
order : ['7.50', '4.25', '4.25', '3.20', '1.80']
page 2: http://testserver/api/products/
```

Read the page shape: DRF's `PageNumberPagination` wraps the list in `{"count", "next", "previous", "results"}`. The number of queries stays small and fixed because the viewset uses `select_related`. Now writes, and the answers for people who may not write (the block hides the framework's log lines for the failed requests):

```python run
import play
from django.contrib.auth.models import Permission, User
from rest_framework.test import APIClient

payload = {"name": "Gadget", "sku": "gd-1", "category": 1, "price": "9.99", "quantity": 9999}

anon = APIClient()
r = anon.post("/api/products/", payload, format="json")
print("anonymous POST :", r.status_code, r.json())

reader = User.objects.create_user("reader", password="pw-reader-123")
api = APIClient(); api.force_authenticate(reader)
r = api.post("/api/products/", payload, format="json")
print("logged in, no perm:", r.status_code, r.json())

writer = User.objects.create_user("writer", password="pw-writer-123")
writer.user_permissions.add(*Permission.objects.filter(codename__in=["add_product", "change_product"]))
api = APIClient(); api.force_authenticate(writer)

r = api.post("/api/products/", {**payload, "price": "-1"}, format="json")
print("invalid POST   :", r.status_code, r.json())

r = api.post("/api/products/", payload, format="json")
print("valid POST     :", r.status_code, r.json())
new_id = r.json()["id"]

r = api.post("/api/products/", {**payload, "sku": " Gd-1 "}, format="json")
print("duplicate SKU  :", r.status_code, r.json())

r = api.patch(f"/api/products/{new_id}/", {"price": "11.50"}, format="json")
print("PATCH          :", r.status_code, r.json()["price"])
r = api.delete(f"/api/products/{new_id}/")
print("DELETE (no perm):", r.status_code)
```
```text
anonymous POST : 403 {'detail': 'Authentication credentials were not provided.'}
logged in, no perm: 403 {'detail': 'You do not have permission to perform this action.'}
invalid POST   : 400 {'price': ['Price must be above zero.']}
valid POST     : 201 {'id': 14, 'name': 'Gadget', 'sku': 'GD-1', 'category': 1, 'category_name': 'Cables', 'price': '9.99', 'quantity': 0, 'reorder_level': 5, 'is_low': True}
duplicate SKU  : 400 {'sku': ['A product with this SKU already exists.']}
PATCH          : 200 11.50
DELETE (no perm): 403
```

Four lessons are visible in this output:

1. **401 versus 403.** The anonymous request got `403` with "Authentication credentials were not provided." DRF answers `401` (with a `WWW-Authenticate` header) only when the *first* authentication class can challenge, as Basic or token authentication do; `SessionAuthentication` cannot, so it answers `403`. Know which one your clients expect.
2. **A bad request is `400` with a dictionary of field errors** (the shape of section 15.2).
3. The valid request sent `quantity: 9999`, yet the new product has `quantity: 0`: `read_only_fields` silently drops the value. The duplicate request (same SKU with spaces and other casing) was caught by our `validate_sku` as a clean `400`.
4. `DjangoModelPermissionsOrAnonReadOnly` reused the same `add_product`, `change_product` and `delete_product` permissions as the HTML views and the admin: **one permission system for three front doors**. The writer may add and change, but `DELETE` is `403`.

### 15.5 What DRF gives and what it does not

- **Content negotiation and the browsable API:** open the same URL in a browser and you get an HTML page with forms; ask for JSON and you get JSON. Handy for exploring and teaching.
- **Throttling** (`DEFAULT_THROTTLE_CLASSES`) limits requests per user or IP; **versioning**, **filtering with `django-filter`**, **token or JWT authentication** are separate or add-on features (swe.07).
- **API schema/docs:** generated with extra packages (`drf-spectacular`). Unlike FastAPI, it is not automatic.
- **Async:** DRF views are synchronous. If your API is mostly I/O waiting on other services, that is one reason to pick FastAPI (section 19).

### Try it: why is `quantity` ignored?

Someone sends `PATCH /api/products/3/` with `{"quantity": 1000}` and sees `200` with the old quantity. A teammate says "DRF has a bug". Explain what happens and what the design intends.

<details><summary>Answer</summary>

`quantity` is in `read_only_fields`, so the serializer **ignores** the input value without an error. This is DRF's default for read-only fields (the response is 200 with the unchanged object). It is deliberate: stock must change only through audited stock movements (section 18). If you prefer a loud failure, validate in `to_internal_value` or in the view and reject unknown or read-only keys with a `400`.

</details>

## 16. Middleware, signals and management commands

Three more Django tools that appear in nearly every real project.

### 16.1 Middleware

**Middleware** is code that wraps every request and response (section 1.3). Each one is a function that receives `get_response` (the next layer) and returns a handler:

```python run
import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=["testserver"],
    SECRET_KEY="x" * 50,
    MIDDLEWARE=["__main__.outer", "__main__.inner"],
)
django.setup()

from django.http import HttpResponse
from django.test import Client
from django.urls import path


def make_layer(name):
    def layer(get_response):
        def middleware(request):
            print(f"  {name}: before the view")
            response = get_response(request)          # goes inward (next middleware, then the view)
            print(f"  {name}: after the view")
            response["X-Seen-By"] = response.get("X-Seen-By", "") + name + " "
            return response
        return middleware
    return layer

outer = make_layer("outer")
inner = make_layer("inner")


def view(request):
    print("  VIEW runs")
    return HttpResponse("ok")

urlpatterns = [path("", view)]

r = Client().get("/")
print(r.status_code, repr(r["X-Seen-By"]))
```
```text
  outer: before the view
  inner: before the view
  VIEW runs
  inner: after the view
  outer: after the view
200 'inner outer '
```

The request passes through the list **top to bottom** (`outer`, `inner`, view) and the response comes back **bottom to top** (`inner`, `outer`), like an onion. A middleware may also return its own response without calling `get_response` (a block, a cache hit). That is why order matters in `MIDDLEWARE`: `SessionMiddleware` must come before `AuthenticationMiddleware`, because authentication reads the session.

For the project, a useful middleware tags every response with a request id for log tracing:

```python
# inventory/middleware.py
import logging
import uuid

logger = logging.getLogger("inventory.requests")


class RequestIdMiddleware:
    def __init__(self, get_response):        # runs once, at server start
        self.get_response = get_response

    def __call__(self, request):             # runs for every request
        request.request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:12]
        response = self.get_response(request)
        response["X-Request-Id"] = request.request_id
        logger.info("%s %s -> %s [%s]", request.method, request.path, response.status_code, request.request_id)
        return response
```

```bash run
sed -i "s/    'django.middleware.security.SecurityMiddleware',/    'django.middleware.security.SecurityMiddleware',\n    'inventory.middleware.RequestIdMiddleware',/" inventory_site/settings.py
python manage.py check
```
```text
System check identified no issues (0 silenced).
```

```python run
from play import client

r = client.get("/products/")
print(r.status_code, len(r["X-Request-Id"]), "chars")
r = client.get("/products/", headers={"X-Request-Id": "trace-me-123"})
print(r["X-Request-Id"])
```
```text
200 12 chars
trace-me-123
```

### 16.2 Signals

A **signal** lets one part of the code announce an event ("a row was saved") and other parts react, without the first knowing about the second. The common ones: `pre_save`, `post_save`, `pre_delete`, `post_delete`, `m2m_changed`, `request_finished`.

```python run
from sandbox import *
from django.db.models.signals import post_save
from django.dispatch import receiver

class Item(models.Model):
    name = models.CharField(max_length=30)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"

@receiver(post_save, sender=Item)
def announce_low_stock(sender, instance, created, **kwargs):
    state = "created" if created else "updated"
    print(f"  [signal] {instance.name} {state}, quantity={instance.quantity}")

create_tables(Item)
print("create():")
a = Item.objects.create(name="pen", quantity=3)
print("save():")
a.quantity = 1
a.save()
print("bulk_create():")
Item.objects.bulk_create([Item(name="ink", quantity=1)])
print("update():")
Item.objects.filter(name="pen").update(quantity=0)
```
```text
create():
  [signal] pen created, quantity=3
save():
  [signal] pen updated, quantity=1
bulk_create():
update():
```

Signals fire from `save()` and `delete()`, and **not** from `bulk_create`, `update()` or raw SQL. This is the main reason many teams avoid them for business rules: the rule works until somebody uses a bulk operation. Guidelines:

- Prefer an **explicit function call** (`record_movement(...)`, section 18) for business logic: it is visible in the code that calls it and easy to test.
- Use signals for **decoupled side effects**, such as clearing a cache or writing an audit line, especially when the signal sender lives in someone else's app (you cannot edit `User.save()`).
- Register receivers in `AppConfig.ready()` (importing the module that defines them), otherwise they never connect.

### 16.3 Management commands

Anything you would run by hand or from `cron` belongs in a **management command**: a Python class in `<app>/management/commands/<name>.py`, run as `python manage.py <name>`. It gets Django set up (settings, ORM) and argument parsing for free.

```bash run
mkdir -p inventory/management/commands
touch inventory/management/__init__.py inventory/management/commands/__init__.py
```
```text
```

```python
# inventory/management/commands/low_stock_report.py
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
```

```bash run
python manage.py low_stock_report
python manage.py low_stock_report --category nonsense 2>&1; echo "exit code: $?"
python manage.py low_stock_report --help | head -12
```
```text
X-0      Extra 0                 0 / 5
X-1      Extra 1                 0 / 5
X-2      Extra 2                 0 / 5
X-3      Extra 3                 0 / 5
X-4      Extra 4                 0 / 5
X-5      Extra 5                 0 / 5
X-6      Extra 6                 0 / 5
GD-1     Gadget                  0 / 5
CB-SPL   Splitter                3 / 5
CB-SP2   Splitter 2              3 / 5
done
CommandError: No low-stock products in category 'nonsense'.
exit code: 1
usage: manage.py low_stock_report [-h] [--category CATEGORY] [--limit LIMIT]
                                  [--version] [-v {0,1,2,3}]
                                  [--settings SETTINGS]
                                  [--pythonpath PYTHONPATH] [--traceback]
                                  [--no-color] [--force-color] [--skip-checks]

Print the products whose stock is at or below their reorder level.

options:
  -h, --help            show this help message and exit
  --category CATEGORY   only this category name
  --limit LIMIT
```

(`self.style.SUCCESS` adds colour in a terminal; there are no colour codes in a pipe.) Commands are ideal for nightly jobs (clean-up, imports, reports) and for one-off data fixes: they are testable with `call_command("low_stock_report", stdout=out)` and kept in version control, unlike a shell session that nobody remembers.

### Try it: which one?

For each job, choose middleware, a signal, or a management command: (a) add a `Content-Security-Policy` header to every response; (b) email the warehouse when a product row is saved with quantity 0; (c) import 10,000 products from a CSV every night.

<details><summary>Answer</summary>

(a) Middleware: it touches every response. (b) A signal would work, but the cleaner design is to put the email in the service function that changes stock (section 18), inside `transaction.on_commit`, so a bulk update cannot skip it and a rolled-back change does not send mail. (c) A management command, started by cron or a scheduler.

</details>

## 17. Security checklist and deployment

### 17.1 What Django protects for you

| Attack | Django's default defence | Where you can still break it |
|---|---|---|
| **SQL injection** | the ORM sends values as parameters | f-strings in `raw()`, `extra()`, `cursor.execute()` |
| **XSS** (script injection) | templates escape variables | `\|safe`, `mark_safe`, building HTML by hand |
| **CSRF** | token in forms plus `CsrfViewMiddleware` | `@csrf_exempt` on a form view, no `{% csrf_token %}` |
| **Clickjacking** | `X-Frame-Options: DENY` header | removing the middleware |
| **Host-header attacks** | `ALLOWED_HOSTS` | `ALLOWED_HOSTS = ["*"]` in production |
| **Weak passwords / leaks** | slow hashes, validators | custom code that stores or logs raw passwords |
| **Session theft** | `HttpOnly` cookie by default | missing `SESSION_COOKIE_SECURE` over HTTPS |

SQL injection deserves one look, because the same mistake exists in every framework:

```python run
from catalog import *

create_tables(Product)
Product.objects.create(name="Pen", sku="P1", price="1")
Product.objects.create(name="Secret", sku="S1", price="999")

name = "x' OR '1'='1"                       # what an attacker types into a search box

unsafe = Product.objects.raw(f"SELECT * FROM shop_product WHERE name = '{name}'")
print("f-string raw():  ", [p.name for p in unsafe])

safe = Product.objects.raw("SELECT * FROM shop_product WHERE name = %s", [name])
print("parameterised:   ", [p.name for p in safe])

print("ORM filter():    ", [p.name for p in Product.objects.filter(name=name)])
```
```text
f-string raw():   ['Pen', 'Secret']
parameterised:    []
ORM filter():     []
```

The f-string turned the attacker's text into SQL and returned **every row**. The parameterised version, and the ORM, treat it as a harmless value. The rule: never build SQL with string formatting; pass values separately (`raw(sql, params)`, `cursor.execute(sql, params)`).

### 17.2 `check --deploy`

Django can audit your settings for production. With the development settings of our project:

```bash run
python manage.py check --deploy
```
```text
SystemCheckError: System check identified some issues:

ERRORS:
?: (mail.E001) Your MAILERS setting uses a development-only email backend in the 'default' entry (django.core.mail.backends.console.EmailBackend).
	HINT: Use a production-ready email backend, such as the SMTP backend, otherwise email will not be sent.

WARNINGS:
?: (security.W004) You have not set a value for the SECURE_HSTS_SECONDS setting. If your entire site is served only over SSL, you may want to consider setting a value and enabling HTTP Strict Transport Security. Be sure to read the documentation first; enabling HSTS carelessly can cause serious, irreversible problems.
?: (security.W008) Your SECURE_SSL_REDIRECT setting is not set to True. Unless your site should be available over both SSL and non-SSL connections, you may want to either set this setting True or configure a load balancer or reverse-proxy server to redirect all connections to HTTPS.
?: (security.W009) Your SECRET_KEY has less than 50 characters, less than 5 unique characters, or it's prefixed with 'django-insecure-' indicating that it was generated automatically by Django. Please generate a long and random value, otherwise many of Django's security-critical features will be vulnerable to attack.
?: (security.W012) SESSION_COOKIE_SECURE is not set to True. Using a secure-only session cookie makes it more difficult for network traffic sniffers to hijack user sessions.
?: (security.W016) You have 'django.middleware.csrf.CsrfViewMiddleware' in your MIDDLEWARE, but you have not set CSRF_COOKIE_SECURE to True. Using a secure-only CSRF cookie makes it more difficult for network traffic sniffers to steal the CSRF token.
?: (security.W018) You should not have DEBUG set to True in deployment.
?: (security.W020) ALLOWED_HOSTS must not be empty in deployment.

System check identified 8 issues (0 silenced).
```

Each warning has an id (`security.W004`, ...) you can look up. Read the output from the top. The **error** is new in Django 6.1: the default `MAILERS` setting uses the console email backend, which only prints mail and is refused for production. Then come the warnings about HTTPS, the cookies, the generated `SECRET_KEY`, `DEBUG` and `ALLOWED_HOSTS`. Instead of editing the development file, production usually gets its own settings module that imports the base and overrides what must differ, with secrets from the environment:

```python
# inventory_site/prod_settings.py
import os

from .settings import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ["DJANGO_ALLOWED_HOSTS"].split(",")

SECURE_SSL_REDIRECT = True                 # send http:// to https://
SESSION_COOKIE_SECURE = True               # cookies only over https
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000             # tell browsers: https only, for a year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

MAILERS = {                                # Django 6.1: the console backend is rejected in production
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {"host": os.environ.get("SMTP_HOST", "smtp.example.com"), "port": 587, "use_tls": True},
    },
}
```

```bash run
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(60))')"
export DJANGO_ALLOWED_HOSTS="shop.example.com"
python manage.py check --deploy --settings=inventory_site.prod_settings
```
```text
System check identified no issues (0 silenced).
```

Before going live you would also set `SECURE_PROXY_SSL_HEADER` if a proxy terminates HTTPS in front of Django (otherwise Django thinks every request is plain HTTP and redirects forever). Only turn on HSTS preload when you are sure the whole domain will stay on HTTPS.

### 17.3 From `runserver` to production

`runserver` is for development only. A production setup has these parts:

```text
 browser --https--> reverse proxy (nginx, a cloud load balancer)
                         |  static files served directly
                         v
              application server: gunicorn (WSGI)  or  uvicorn/daphne (ASGI)
                         |
                      Django project  --->  PostgreSQL
```

| Concern | What to do |
|---|---|
| App server | `gunicorn inventory_site.wsgi:application --workers 3` (WSGI) or `uvicorn inventory_site.asgi:application` (ASGI) |
| Static files | `python manage.py collectstatic` copies them into `STATIC_ROOT`; nginx or WhiteNoise serves them |
| Media (uploads) | separate storage (disk, object storage), never in the repository |
| Database | PostgreSQL (`psycopg`), with connection settings from the environment; backups |
| Migrations | run `migrate` once per release, before starting the new version |
| Secrets | environment variables or a secret manager, never in git |
| Logging | `LOGGING` setting to stdout or files; do not rely on `print` |
| Debugging | `DEBUG = False`; send errors to a monitoring tool; never show tracebacks to visitors |

> **Try it on your machine** (needs PostgreSQL and `pip install psycopg[binary]`, so it is not run here)
>
> ```python
> DATABASES = {
>     "default": {
>         "ENGINE": "django.db.backends.postgresql",
>         "NAME": os.environ["DB_NAME"],
>         "USER": os.environ["DB_USER"],
>         "PASSWORD": os.environ["DB_PASSWORD"],
>         "HOST": os.environ.get("DB_HOST", "localhost"),
>         "PORT": "5432",
>     }
> }
> ```
>
> Then `python manage.py migrate` creates the same tables in PostgreSQL. Your models and queries do not change; this is the ORM's promise. Differences you will meet: stricter types, real row locks for `select_for_update()`, and case-sensitive `LIKE` unless you use `icontains`.

Django also supports **async views** and an async ORM interface (`await Product.objects.aget(...)`, `async for p in qs`) under ASGI. The ORM still talks to a normal database driver underneath, so async helps when a view waits on other services, not because queries become faster. For an API that is mostly I/O orchestration, section 19 explains why FastAPI is often the better fit.

### Try it: the missing `check`

A teammate deploys with `DEBUG = True` "just for a day, to see errors". Name two things an attacker gains.

<details><summary>Answer</summary>

(1) The technical error page shows source code, settings values (with secrets partly hidden but much exposed), SQL queries and environment details to anyone who triggers an error. (2) With `DEBUG = True`, Django keeps every SQL query in memory (a slow leak under load) and, with an empty `ALLOWED_HOSTS`, accepts any host name. Use a log tool or Sentry-like service for errors; never show them to visitors.

</details>


## 18. Project: an admin-driven inventory app, step by step

We finish the **inventory app** that has grown through the chapter. It is "admin-driven": staff do their daily work in the Django admin, and other systems use a small API. The rules, which the tests will enforce:

- Staff manage **categories and products** in the admin.
- The stock count of a product is **never edited directly**. It changes only through **stock movements** (goods received, a sale, a stock-take adjustment), and every movement records **who** did it and **why**.
- A movement can **never make stock negative**.
- Movements cannot be edited or deleted afterwards (an audit trail).
- An API lets other systems read products and low-stock lists, and lets permitted users record movements.

If you get stuck, the finished project is in `docs/reference/swe.06-django-inventory/` (compare it with your own; do not copy it first).

What exists already: project and app (2), models Category and Product with migrations (8), admin (10), forms and generic views (11, 12), login and permissions (13), tests (14), DRF read/write products (15), a report command (16). Now we add the stock movements.

### Step 1: the movement model

```python
# inventory/models.py
from django.conf import settings
from django.db import models
from django.db.models import F
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def low_stock(self):
        return self.filter(quantity__lte=F("reorder_level"))


class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField("SKU", max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse("inventory:product-detail", kwargs={"pk": self.pk})

    @property
    def is_low(self):
        return self.quantity <= self.reorder_level


class StockMovement(models.Model):
    class Reason(models.TextChoices):
        RECEIVE = "receive", "Goods received"
        SALE = "sale", "Sale"
        ADJUST = "adjust", "Stock-take adjustment"

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="movements")
    delta = models.IntegerField(help_text="Positive adds stock, negative removes it.")
    reason = models.CharField(max_length=20, choices=Reason)
    note = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="+")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created", "-id"]
        constraints = [
            models.CheckConstraint(condition=~models.Q(delta=0), name="movement_delta_not_zero"),
        ]

    def __str__(self):
        return f"{self.product.sku} {self.delta:+d} ({self.reason})"
```

Design choices worth defending: `PROTECT` on the product (history must not vanish when someone deletes a product), `SET_NULL` on the user (removing an employee must not remove their movements), and the `CheckConstraint` so even a script cannot insert a movement of zero units.

```bash run
python manage.py makemigrations inventory
python manage.py migrate inventory
```
```text
Migrations for 'inventory':
  inventory/migrations/0004_stockmovement.py
    + Create model StockMovement
Operations to perform:
  Apply all migrations: inventory
Running migrations:
  Applying inventory.0004_stockmovement... OK
```

### Step 2: one function that changes stock

All stock changes go through **one** function. The admin, the API and the shell all call it, so the rules live in one place and one test file:

```python
# inventory/services.py
from django.db import transaction
from django.db.models import F

from .models import Product, StockMovement


class InsufficientStock(Exception):
    def __init__(self, product, wanted, available):
        super().__init__(f"Cannot remove {wanted} of {product.sku}: only {available} in stock.")
        self.product, self.wanted, self.available = product, wanted, available


@transaction.atomic
def record_movement(product, delta, reason, *, user=None, note=""):
    """Change a product's stock and record why. All or nothing."""
    if delta == 0:
        raise ValueError("A movement of zero units is meaningless.")
    rows = Product.objects.filter(pk=product.pk)
    if delta < 0:
        rows = rows.filter(quantity__gte=-delta)          # refuse to go below zero, inside the UPDATE
    if rows.update(quantity=F("quantity") + delta) == 0:
        product.refresh_from_db(fields=["quantity"])
        raise InsufficientStock(product, -delta, product.quantity)
    product.refresh_from_db(fields=["quantity"])
    return StockMovement.objects.create(product=product, delta=delta, reason=reason, note=note, created_by=user)
```

Check the choices against sections 9.3 and 6.4: the stock arithmetic is a single `UPDATE ... SET quantity = quantity + delta WHERE quantity >= wanted`, so two simultaneous sales cannot both succeed on the last unit; `atomic()` makes the update and the history row succeed or fail together; the function reports a missing-stock problem with a **specific exception**, which each caller turns into the right response (an admin message, an HTTP 409).

Since quantity is now controlled by movements, take it out of the edit form too:

```python
# inventory/forms.py
from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "category", "price", "reorder_level"]      # no quantity: use movements

    def clean_sku(self):
        return self.cleaned_data["sku"].strip().upper()

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Price must be above zero.")
        return price
```

### Step 3: the admin

```python
# inventory/admin.py
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
```

Two ideas to notice: `readonly_fields` removes the quantity from the edit form, and the `has_*_permission` methods enforce the audit trail even for superusers. Staff can still change stock, through the action, which goes through `record_movement` and records who did it.

### Step 4: the API

The serializer for movements, and the viewset with two extra actions:

```python
# inventory/serializers.py
from rest_framework import serializers

from .models import Category, Product, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_low = serializers.BooleanField(read_only=True)
    sku = serializers.CharField(max_length=20, validators=[])      # uniqueness is checked by hand below

    class Meta:
        model = Product
        fields = ["id", "name", "sku", "category", "category_name", "price", "quantity", "reorder_level", "is_low"]
        read_only_fields = ["quantity"]            # quantity changes only through stock movements

    def validate_sku(self, value):
        value = value.strip().upper()
        others = Product.objects.filter(sku=value)
        if self.instance is not None:
            others = others.exclude(pk=self.instance.pk)
        if others.exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be above zero.")
        return value


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ["id", "product", "delta", "reason", "note", "created"]
        read_only_fields = ["id", "product", "created"]

    def validate_delta(self, value):
        if value == 0:
            raise serializers.ValidationError("Delta must not be zero.")
        return value
```

```python
# inventory/api.py
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
```

The HTTP choice to defend: running out of stock is not a *malformed* request (400), but a conflict with the *current state* of the resource, so `409 Conflict` tells the client "the request was fine; the state does not allow it". The URL `POST /api/products/7/movements/` treats a movement as a sub-resource of the product, in REST style (swe.02).

### Step 5: tests that prove the rules

```python
# inventory/test_stock.py
from unittest import mock

from django.contrib.auth.models import Permission, User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Category, Product, StockMovement
from .services import InsufficientStock, record_movement

RECEIVE, SALE = StockMovement.Reason.RECEIVE, StockMovement.Reason.SALE


class StockServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("worker", password="pw-worker-123")
        cat = Category.objects.create(name="Tools")
        self.product = Product.objects.create(name="Hammer", sku="HM-1", category=cat, price="12.00", quantity=10)

    def test_receiving_adds_stock_and_records_who(self):
        m = record_movement(self.product, 5, RECEIVE, user=self.user, note="delivery")
        self.assertEqual(self.product.quantity, 15, "the in-memory product should show the new stock")
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 15)
        self.assertEqual((m.delta, m.created_by), (5, self.user))

    def test_selling_the_last_unit_is_allowed(self):
        record_movement(self.product, -10, SALE)
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 0)

    def test_overselling_is_refused_and_leaves_no_trace(self):
        with self.assertRaises(InsufficientStock) as ctx:
            record_movement(self.product, -11, SALE)
        self.assertEqual((ctx.exception.wanted, ctx.exception.available), (11, 10))
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 10, "stock must be unchanged")
        self.assertEqual(StockMovement.objects.count(), 0, "no movement row for a refused sale")

    def test_a_failure_after_the_update_rolls_the_stock_back(self):
        with mock.patch.object(StockMovement.objects, "create", side_effect=RuntimeError("disk full")):
            with self.assertRaises(RuntimeError):
                record_movement(self.product, -3, SALE)
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 10, "atomic() should undo the UPDATE")

    def test_zero_movement_is_a_programming_error(self):
        with self.assertRaises(ValueError):
            record_movement(self.product, 0, RECEIVE)

    def test_database_rejects_zero_delta_even_without_the_service(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            StockMovement.objects.create(product=self.product, delta=0, reason=RECEIVE)

    def test_stock_equals_start_plus_sum_of_movements(self):
        for delta in (4, -3, 20, -7):
            record_movement(self.product, delta, RECEIVE if delta > 0 else SALE)
        total = sum(m.delta for m in StockMovement.objects.all())
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 10 + total)


class MovementApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Tools")
        cls.product = Product.objects.create(name="Saw", sku="SW-1", category=cat, price="20.00", quantity=3, reorder_level=5)
        Product.objects.create(name="Nails", sku="NL-1", category=cat, price="1.00", quantity=500, reorder_level=50)
        cls.clerk = User.objects.create_user("clerk", password="pw-clerk-123")
        cls.clerk.user_permissions.add(Permission.objects.get(codename="add_stockmovement"))
        cls.url = f"/api/products/{cls.product.pk}/movements/"

    def test_anonymous_cannot_record(self):
        r = APIClient().post(self.url, {"delta": 1, "reason": "receive"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_user_without_permission_cannot_record(self):
        api = APIClient()
        api.force_authenticate(User.objects.create_user("plain", password="pw-plain-123"))
        self.assertEqual(api.post(self.url, {"delta": 1, "reason": "receive"}, format="json").status_code, 403)

    def test_clerk_records_a_sale(self):
        api = APIClient(); api.force_authenticate(self.clerk)
        r = api.post(self.url, {"delta": -2, "reason": "sale", "note": "web order"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 1)
        self.assertEqual(StockMovement.objects.get().created_by, self.clerk)

    def test_overselling_returns_409_and_changes_nothing(self):
        api = APIClient(); api.force_authenticate(self.clerk)
        r = api.post(self.url, {"delta": -4, "reason": "sale"}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertIn("only 3 in stock", r.json()["detail"])
        self.assertEqual(Product.objects.get(pk=self.product.pk).quantity, 3)

    def test_bad_input_returns_400(self):
        api = APIClient(); api.force_authenticate(self.clerk)
        r = api.post(self.url, {"delta": 0, "reason": "gift"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(sorted(r.json()), ["delta", "reason"])

    def test_low_stock_list_is_correct_and_cheap(self):
        with self.assertNumQueries(2):                       # COUNT + SELECT (category joined)
            r = APIClient().get("/api/products/low-stock/")
        self.assertEqual([p["sku"] for p in r.json()["results"]], ["SW-1"])


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("boss", password="pw-boss-12345")
        cat = Category.objects.create(name="Tools")
        cls.product = Product.objects.create(name="Saw", sku="SW-1", category=cat, price="20.00", quantity=3)

    def setUp(self):
        self.client.force_login(self.admin)

    def test_quantity_is_not_editable_in_the_admin(self):
        r = self.client.get(reverse("admin:inventory_product_change", args=[self.product.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('name="quantity"', r.content.decode(), "quantity must be read-only")
        before = self.product.quantity
        self.client.post(reverse("admin:inventory_product_change", args=[self.product.pk]),
                         {"name": "Saw", "sku": "SW-1", "category": self.product.category_id, "price": "20.00",
                          "reorder_level": 5, "quantity": 999, "movements-TOTAL_FORMS": 0, "movements-INITIAL_FORMS": 0})
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, before, "a forged quantity must be ignored")

    def test_receive_action_goes_through_the_service(self):
        r = self.client.post(reverse("admin:inventory_product_changelist"),
                             {"action": "receive_10", "_selected_action": [self.product.pk]})
        self.assertEqual(r.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 13)
        self.assertEqual(StockMovement.objects.get().created_by, self.admin)

    def test_movements_cannot_be_added_or_deleted_even_by_a_superuser(self):
        self.assertEqual(self.client.get(reverse("admin:inventory_stockmovement_add")).status_code, 403)
        m = record_movement(self.product, 1, RECEIVE)
        self.assertEqual(self.client.post(reverse("admin:inventory_stockmovement_delete", args=[m.pk]), {"post": "yes"}).status_code, 403)
        self.assertTrue(StockMovement.objects.filter(pk=m.pk).exists())
```

### Step 6: run everything

```bash run
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```
```text
System check identified no issues (0 silenced).
No changes detected
Found 25 test(s).
System check identified no issues (0 silenced).
Creating test database for alias 'default'...
.........................
----------------------------------------------------------------------
Ran 25 tests in 5.800s

OK
Destroying test database for alias 'default'...
```

We also checked that the tests are not decorative: we broke the code on purpose in a copy of the project and each break was caught. Removing the `quantity__gte` guard failed the two overselling tests; making `quantity` editable in the admin failed the admin test; changing `409` to `400` failed the API test; removing `select_related` from the list view failed the query-count test; and removing `@transaction.atomic` failed the rollback test. A test that cannot fail proves nothing, so try this on your own tests (core.08, core.19).

The first run of a new test file is the moment to read failures as design feedback. Good habits: each test name states the rule; one assertion message names the likely mistake (`"stock must be unchanged"`); security rules (`test_user_without_permission_cannot_record`) get their own tests. Finally, the report command from section 16 now works on movement-driven data, and we can look at the whole project:

```bash run
python manage.py shell --no-imports -c "
from inventory.models import Product, StockMovement
from inventory.services import record_movement
p = Product.objects.get(sku='CB-AUX')
print('before:', p.quantity, 'low' if p.is_low else 'ok')
record_movement(p, 50, StockMovement.Reason.RECEIVE, note='shell restock')
print('after: ', p.quantity, 'low' if p.is_low else 'ok')
print(StockMovement.objects.filter(product=p).values_list('delta', 'reason', 'note'))
"
find inventory inventory_site -name '*.py' -not -path '*__pycache__*' | sort
```
```text
before: 4 low
after:  54 ok
<QuerySet [(50, 'receive', 'shell restock')]>
inventory/admin.py
inventory/api.py
inventory/apps.py
inventory/forms.py
inventory/__init__.py
inventory/management/commands/__init__.py
inventory/management/commands/low_stock_report.py
inventory/management/__init__.py
inventory/middleware.py
inventory/migrations/0001_initial.py
inventory/migrations/0002_product_reorder_level.py
inventory/migrations/0003_normalise_skus.py
inventory/migrations/0004_stockmovement.py
inventory/migrations/__init__.py
inventory/models.py
inventory/serializers.py
inventory/services.py
inventory_site/asgi.py
inventory_site/__init__.py
inventory_site/prod_settings.py
inventory_site/settings.py
inventory_site/urls.py
inventory_site/wsgi.py
inventory/tests.py
inventory/test_stock.py
inventory/urls.py
inventory/views.py
```

#### What to try on your machine

1. `python manage.py createsuperuser`, `python manage.py runserver`, open `http://127.0.0.1:8000/admin/`. Add categories and products, then use the **Receive 10 units** action and open a product to see its history.
2. Open `http://127.0.0.1:8000/api/products/`: the DRF browsable API. Log in with the link at the top right and try `POST` on `/api/products/<id>/movements/` with `{"delta": -1, "reason": "sale"}`.
3. Extend it: add a `supplier` field (a new migration), a CSV import management command that uses `record_movement`, and a test that two concurrent sales of the last unit cannot both succeed (hint: it needs a database with real concurrency, such as PostgreSQL, and `TransactionTestCase`).

## 19. Choosing between Django, Flask and FastAPI

This is the second outcome of the chapter: **choose a framework for a project and defend the choice.** There is no best framework. There is a best fit for a given job, team and deadline. Here is how to decide, and how to say why.

### 19.1 What each framework gives you

| | Flask (swe.04) | FastAPI (swe.05) | Django (this chapter) |
|---|---|---|---|
| Philosophy | small core, you pick parts | typed API first | batteries included |
| Protocol | WSGI (async limited) | ASGI, async first | WSGI and ASGI, mostly sync in practice |
| Database layer | none (SQLAlchemy usual) | none (SQLAlchemy / SQLModel usual) | built-in ORM and migrations |
| Admin UI for data | extension (Flask-Admin) | you build it | **built in** |
| Users, sessions, permissions | extensions | you build it (see swe.05 section 12) | **built in** |
| HTML pages and forms | Jinja2 + extensions | possible, not the focus | **built in** (templates, forms) |
| JSON validation and docs | by hand / extensions | **built in** (Pydantic, OpenAPI) | DRF (serializers); docs need extra packages |
| WebSockets, streaming | extensions | **built in** | Channels (add-on) |
| First working feature | very fast | fast | slower setup, then very fast CRUD |
| Learning curve | gentle, but you assemble the rest | gentle for APIs, steeper with async | steepest at the start, most consistent afterwards |
| Project structure | your choice | your choice | **conventional**, familiar to every Django developer |
| Ecosystem and hiring | large | fast-growing | very large and mature |

### 19.2 Five questions to ask

1. **Who or what is the user?** Staff clicking through data screens and customers in browsers lean Django. Other programs (mobile apps, single-page front ends, services) lean FastAPI or DRF.
2. **Is the data model the heart of the project?** Many related tables edited by non-programmers, with permissions and an audit trail: Django's ORM, migrations and admin give weeks of work for free.
3. **Is the work mostly waiting?** An endpoint that mostly calls other services, streams, or holds thousands of idle connections (chat, notifications) benefits from async: FastAPI. Heavy CPU work is a problem for every Python web framework; it belongs in a worker or task queue.
4. **How much do you want to decide yourself?** Every part you choose is a part you must integrate, secure and maintain. Django's defaults are reviewed by thousands of projects; your own assembly is reviewed by you. For experienced teams with special needs that freedom is valuable. For a small team with a deadline it is a cost.
5. **What is the life of the project and the team?** A system that lives for years with changing developers benefits from Django's conventions. A throw-away prototype or a single-purpose service can use whatever is quickest.

Performance deserves a warning. In most real applications the bottleneck is the database and the network, not the framework. Choosing by micro-benchmarks is a common mistake; choose by the questions above, then fix measured bottlenecks (indexes, `select_related`, caching), as you practised in swe.03 and this chapter.

### 19.3 Seven scenarios

| # | The job | A good choice | Why | What would change the answer |
|---|---|---|---|---|
| A | Internal tool for 3 warehouse staff to manage products and stock, due in 2 weeks | **Django** | the admin, auth and ORM *are* the product; section 18 took one file per layer | none really; maybe a spreadsheet is enough |
| B | Public JSON API for a mobile app, 500 concurrent clients, calls an ML model service | **FastAPI** | API only, async I/O, typed validation and automatic docs | if the team already runs Django, use DRF and scale workers |
| C | One webhook that posts a message to a chat tool | **Flask** or **FastAPI** (one file) | tiny; any framework is more than enough | if more endpoints and validation appear, FastAPI |
| D | Content site: accounts, comments, moderators, SEO pages, an editor interface | **Django** | templates, forms, auth, admin and permissions all needed | a pure single-page app front end makes it an API job again |
| E | Service that combines 5 other APIs per request and must stay fast | **FastAPI** | `async`/`httpx` run the 5 calls concurrently (core.21) | if each call is fast and local, any framework works |
| F | Start-up MVP: customer web app, ops back office, mobile API | **Django + DRF** | admin for ops is free, the same models serve web and API | later, split a hot path into a FastAPI service if measurements show the need |
| G | An existing Django shop needs live order notifications | **Keep Django**, add Channels or a small FastAPI service | do not rewrite working code for one feature | if the real-time part grows into most of the product |

Notice what the table does **not** say: "Django is slow" or "FastAPI is modern". Each choice rests on the job, the data, the team and the cost of the alternative.

### 19.4 How to defend a choice

A defence has four parts, and a reviewer should be able to disagree with any one of them on facts:

1. **The job** in one sentence (who uses it, what is the data).
2. **The choice and the reasons** tied to that job.
3. **The cost you accept** (every choice has one).
4. **The trigger to revisit** (what measurement or change would make you reconsider).

Example, scenario A: "We build an internal stock tool for three staff in two weeks. We choose Django because the admin, authentication and migrations give us the whole back office without writing it, and the stock rules fit in one service function with tests. We accept that Django is heavier than a micro-framework and that async is not its strength. We would revisit if the tool became a public, high-traffic API."

Weak defences to avoid: "everyone uses it", "it is faster" with no measurement, "I already know it" (a legitimate input, but say it as a cost and a benefit, not as the reason), and "it is newer".

Frameworks also **combine** well. Django can own the data and the admin while a small FastAPI service handles a hot path; both can talk to the same database or to each other over HTTP. The concepts you learned (HTTP, ORM sessions, validation, dependency injection, tokens, tests) carry from one to the other, so a wrong first choice costs less than it feels like.

### Try it: choose and defend

For each job, write the four-part defence in your own words before you open the answer. (a) A school needs a site where teachers enter marks, students see their results and the principal prints reports. (b) A weather start-up exposes a read-only API that answers 2,000 requests per second from cached data. (c) A solo developer needs one endpoint that receives a payment webhook and updates a row.

<details><summary>Answer</summary>

(a) **Django.** The job is a data-entry system with roles (teachers write, students read, principal reports). Django gives the ORM and migrations for marks and students, groups and permissions for the roles, the admin for data fixes, and templates and forms for the pages. Cost: heavier than needed for a trivial site. Revisit: if it must become a mobile-first public API at large scale.

(b) **FastAPI** (or any async framework) with a cache in front. The job is read-heavy, no admin, no forms, no sessions: validation and documentation matter and the work is I/O. Cost: you build auth, migrations and admin yourself, and you must keep the event loop free of blocking calls (swe.05 section 10). Revisit: if the numbers show the cache and database, not the framework, are the limit.

(c) **Flask or FastAPI**, one file. One endpoint needs no admin, no templates, no ORM beyond a single table. The important work is not the framework: it is verifying the webhook signature and making the handler idempotent (swe.07). Cost: minimal. Revisit: if the service grows beyond a handful of endpoints.

A strong answer also names what would make the opposite choice correct. If your defence cannot say that, you have a preference, not a reason.

</details>

## 20. Common traps

1. **Forgetting to register the app** in `INSTALLED_APPS`: models are not found, no migrations, templates not loaded (2.3).
2. **`null=True` on text fields** (two kinds of "empty") or **`blank=True` without `null=True` on a date or number** (forms accept empty, the database refuses) (6.2).
3. **`FloatField` for money**. Use `DecimalField` (6.2).
4. **N+1 queries** from `obj.relation` in loops, templates, serializers and `list_display` methods. Use `select_related` (one object) and `prefetch_related` (many) and test with `assertNumQueries` (7.4, 10.2, 14).
5. **Counting two relations in one query** without `distinct=True` (7.5).
6. **`len(qs)` or `if qs:` just to count or test existence**; use `count()` and `exists()` (6.6).
7. **Read-modify-write on shared numbers** (`p.quantity -= 1; p.save()`). Use `F()` and `update()` (6.4, 9.5).
8. **Wrong `on_delete`**: `CASCADE` where history must survive (7.1).
9. **Editing or deleting an applied migration**, or **importing real models inside `RunPython`** instead of `apps.get_model` (8.3, 8.5).
10. **A data change without a reverse function** in `RunPython` (8.3).
11. **Assuming `bulk_create`, `update()` and `delete()` call `save()` and signals**; they do not (9.1, 16.2).
12. **Missing `transaction.atomic()`** around multi-step changes (9.3).
13. **`ModelForm` with `fields = "__all__"` or `exclude`**: mass assignment (11.2).
14. **Missing `{% csrf_token %}`** or "fixing" it with `@csrf_exempt` (11.3).
15. **No redirect after a successful POST**, so reload duplicates data (11.3).
16. **`|safe` on user text**: XSS (5.2).
17. **Creating users with `User.objects.create(password=...)`**: stored in plain text. Use `create_user` (13.2).
18. **Forgetting the ownership filter** (`filter(owner=request.user)`): IDOR (13.4).
19. **Starting a project without a custom user model** (13.5).
20. **Importing `from project.settings import X`** instead of `from django.conf import settings` (3.2).
21. **`DEBUG = True` or a committed `SECRET_KEY` in production**; `ALLOWED_HOSTS = ["*"]` (3, 17).
22. **A `%` in an admin action `description`** crashes the list page (10.1).
23. **DRF's `UniqueValidator` runs before your `validate_<field>` normalisation**: duplicates reach the database (15.2).
24. **`read_only_fields` fail silently**: the client sees `200` and an unchanged value (15.4).
25. **Raw SQL built with f-strings**: SQL injection. Pass `params` (17.1).
26. **Testing with only one actor**: access-control bugs stay invisible (14.3).
27. **Using `runserver` in production** (17.3).

## 21. Collected traps

| If you see... | The cause is usually... | Look at |
|---|---|---|
| `Model class ... doesn't declare an explicit app_label and isn't in INSTALLED_APPS` | app not registered | 2.3 |
| `no such table` / `relation does not exist` | migrations not applied (`migrate`) or not created (`makemigrations`) | 8 |
| `You have N unapplied migration(s)` | run `python manage.py migrate` | 8.1 |
| `django.db.utils.IntegrityError: NOT NULL constraint failed` | field without `default` or `null=True` | 6.2, 8.2 |
| `UNIQUE constraint failed` | duplicate value; check before saving or catch `IntegrityError` | 9.2, 9.4 |
| `ProtectedError` | deleting a row that other rows `PROTECT` | 7.1 |
| `DoesNotExist` / `MultipleObjectsReturned` | `get()` expects exactly one row | 6.3 |
| page slow, hundreds of queries | N+1 | 7.4, 14 |
| `TemplateDoesNotExist` | wrong template path, or app missing from `INSTALLED_APPS` | 5.3 |
| `NoReverseMatch` | wrong URL name/namespace, or missing kwargs | 4.3 |
| `403 CSRF verification failed` | missing `{% csrf_token %}` or cookie | 11.3 |
| `DisallowedHost` / `Bad Request (400)` | host name not in `ALLOWED_HOSTS` | 3 |
| `ImproperlyConfigured: settings are not configured` | `DJANGO_SETTINGS_MODULE` missing or `django.setup()` not called | 1.4, 4 |
| `403` for a logged-in user | missing permission; anonymous gets a redirect to login | 13.4 |
| DRF `403` "credentials were not provided" | session auth cannot send `401` | 15.4 |
| DRF `500` `IntegrityError` on create | uniqueness not checked before normalising | 15.2 |
| `ValueError: incomplete format` in the admin | `%` in an action description | 10.1 |
| `check --deploy` errors/warnings | production settings missing (HTTPS, secrets, mail backend) | 17.2 |
| admin list slow | method column touching a relation: add `list_select_related` | 10.2 |

## 22. Summary

- **Django** is a full-stack framework in the MTV pattern: the URLconf routes to **views**, views use **models** (the ORM) and **templates**, and middleware wraps every request.
- A **project** holds settings and URLs; **apps** are features that you register in `INSTALLED_APPS`. `manage.py` runs the server, migrations, shell, tests and your own commands.
- The **ORM** maps classes to tables: `filter`/`exclude`/`get`, lookups with `__`, `Q` and `F`, `aggregate`/`annotate`. QuerySets are lazy and cached; `count()` and `exists()` beat `len()`; `F()` avoids lost updates.
- **Relationships** (`ForeignKey`, `ManyToManyField`, `OneToOneField`) need a considered `on_delete`. **N+1** is fixed with `select_related` and `prefetch_related` and guarded with `assertNumQueries`.
- **Migrations** are version control for the schema: `makemigrations`, `sqlmigrate`, `migrate`; data migrations use `apps.get_model` and a reverse function; never edit applied migrations.
- Write data safely: bulk operations, `get_or_create`, `transaction.atomic()`, and **database constraints**; keep business rules in one service function.
- The **admin** gives staff a back office: `list_display`, filters, search, inlines, actions, permissions. Beware N+1 in method columns.
- **Forms and ModelForms** validate and save; always list `fields`, redirect after POST, keep the CSRF token. **Generic class-based views** do CRUD in a few lines.
- **Authentication** is built in (hashed passwords, sessions, groups, permissions): use `LoginRequiredMixin` / `PermissionRequiredMixin`, filter by owner to avoid IDOR, and decide on a custom user model on day one.
- **Tests:** `TestCase`, the test client, `assertNumQueries`, a test database per run. **DRF** adds serializers, viewsets, routers, permissions and pagination; know `400` versus `401/403` versus `409`.
- **Security and deployment:** the defaults protect you until you bypass them; `check --deploy`, `DEBUG = False`, secrets in the environment, a real app server and static-file plan, PostgreSQL.
- **Choosing a framework** means asking who uses it, how central the data model is, whether the work is waiting, how much you want to decide, and how long it must live. Defend with the job, the reasons, the accepted cost and a trigger to revisit.

Next: the 25 problems for this module practise ORM queries and N+1 counting, reading migrations, model and form validation, permissions, DRF serializers, tracing query counts, fixing a leaky admin or view, and defending framework choices.

# Problem plan: swe.06 Django essentials (25 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `swe.06.p001`…`p025`.

**Mix:** 9 drill, 11 applied, 3 deep, 2 challenge. **Kinds:** 18 code, 5 trace, 2 explain.
**assessment:** explain = p024, trace = p008, fix = p009, build = p025.
**★ core set:** p005, p006, p007, p008, p009, p013, p016, p018, p023, p024, p025 (outcome: choose a framework and defend the choice; plus the MTV/ORM/admin/DRF basics the choice rests on).

**Testing notes: the Django pattern (spiked and measured 2026-11-18)**

The learner's `solution.py` holds models, admin registrations, views, serializers **and** `urlpatterns`; each model says `class Meta: app_label = "shop"` (exactly the chapter's sandbox, Ch. 6.1). The problem's `conftest.py` is the same for every Django problem:

```python
import django, pytest
from django.apps import AppConfig
from django.conf import settings

class ShopConfig(AppConfig):          # a fake app "shop" that owns the learner's models
    name = "conftest"
    label = "shop"

if not settings.configured:
    settings.configure(
        DEBUG=False, SECRET_KEY="test-secret-key-" + "0" * 40, ALLOWED_HOSTS=["testserver"],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        INSTALLED_APPS=["django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
                        "django.contrib.sessions", "django.contrib.messages", "rest_framework",
                        "conftest.ShopConfig"],
        MIDDLEWARE=["django.contrib.sessions.middleware.SessionMiddleware",
                    "django.middleware.common.CommonMiddleware",
                    "django.middleware.csrf.CsrfViewMiddleware",
                    "django.contrib.auth.middleware.AuthenticationMiddleware",
                    "django.contrib.messages.middleware.MessageMiddleware"],
        ROOT_URLCONF="solution",
        TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True,
                    "OPTIONS": {"context_processors": ["django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages"]}}],
        USE_TZ=True, DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],   # fast, tests only
    )
    django.setup()

from django.core.management import call_command
from django.apps import apps
from django.db import connection
import solution                                   # registers the learner's models in app "shop"
call_command("migrate", verbosity=0)              # auth, admin, sessions, contenttypes tables
with connection.schema_editor() as editor:        # the learner's tables (no migrations, Ch. 6.1)
    for model in apps.get_app_config("shop").get_models():
        editor.create_model(model)

@pytest.fixture(autouse=True)
def _rollback():                                  # every test starts from an empty database
    from django.db import transaction
    with transaction.atomic():
        yield
        transaction.set_rollback(True)
```

- Measured under `ulimit -v 1048576`: 5 tests (JSON view, isolation between tests, `login_required` + superuser in the admin changelist, a DRF `ModelViewSet` POST/GET with a query count, CSRF enforced with `Client(enforce_csrf_checks=True)`) **pass in 1.9 s, 95 MB peak**.
- `run_syncdb=True` does **not** work here: Django only syncs apps that have a `models` module, and the fake app has none. Use `schema_editor` as above.
- **Starters must define every name the test imports** (model classes with a placeholder field, views returning `HttpResponse(status=501)`, an empty `urlpatterns`). A starter without the models makes `conftest.py` fail at import → pytest "error during collection" with 0 tests, which `validate` accepts but which is a confusing first screen for the learner.
- Templates: `django.template.Template("...")` strings or a `TEMPLATES` dict rendered with `Engine(loaders=[("django.template.loaders.locmem.Loader", TEMPLATES)])`; `.html` files are not copied (R1). Generic views in p020 set `template_name` and the test settings add a locmem loader for that problem's templates (the problem's conftest variant).
- Query counts with `django.test.utils.CaptureQueriesContext(connection)`. Logins with `client.force_login(user)` (fast) except in the CSRF/login problems.
- Migrations (Ch. 8) are not run by tests (they need an app folder with `migrations/`); p012 is an explain problem, and the project's `solution.md` shows the real `makemigrations` flow from the reference project in `docs/reference/swe.06-django-inventory/`.

## A. Requests, URLs and templates (Ch. 1–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Django in one file ✅ | drill | code | function views and `urlpatterns` with `<int:pk>` and `<slug:slug>` converters (Ch. 1.4, 4.1–4.2); `/items/abc/` → 404; JSON and plain responses |
| 2 | Where does `reverse` point? ✅ | drill | trace | `⚠ HAND-TRACE` a URLconf with `include`, `app_name` namespaces and names; write the result of 6 `reverse(...)` calls, or `NoReverseMatch` |
| 3 | A filter chain ✅ | drill | trace | `⚠ HAND-TRACE` the chapter's "Try it: a filter chain" style: 6 template expressions (`|default`, `|upper|truncatechars:8`, `|date:"Y-m-d"`, `|length`, a missing variable, `|safe` vs escaped `<b>`); write the rendered text |
| 4 | Escaping user content ✅ | drill | code | `render_comment(text)` with a Django `Template`: `<script>` escaped, newlines → `<br>` via `linebreaksbr`, URLs not turned into raw HTML; no `|safe` (Ch. 5.2) |

## B. Models and the ORM (Ch. 6–7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Category and Item models ✅ | drill | code | `Category`, `Item(name unique, sku, quantity PositiveIntegerField, price DecimalField, category FK PROTECT, status choices)`, `__str__`; tests create rows and inspect `_meta` fields |
| 6 | Lookups and `Q` objects ✅ | drill | code | `search(text=None, max_price=None, in_stock=None)` returning a QuerySet: `icontains`, `lte`, `Q(name__icontains=t) | Q(sku__iexact=t)`, `exclude(status="discontinued")`; returns a QuerySet, not a list |
| 7 | Stock value per category ✅ | applied | code | `annotate(value=Coalesce(Sum(F("quantity") * F("price")), 0, output_field=DecimalField()))`; categories without items show 0; ordered by value desc |
| 8 | How many queries? ✅ | applied | trace | `assessment = "trace"`. `⚠ HAND-TRACE` 8 lines with QuerySets (Ch. 6.6, "Try it: how many queries?"): defining, slicing, iterating twice, `len()`, `exists()`, `count()` after evaluation, `first()`; write the cumulative query count after each line |
| 9 | Fix the N+1 on the stock page ✅ | applied | code | `assessment = "fix"`. The view lists items with `item.category.name` and each item's tag names: 1 + 2N queries; fix with `select_related` + `prefetch_related`; ≤ 3 queries for 40 items, same output (Ch. 7.4) |
| 10 | The double-join trap ✅ | deep | code | counting suppliers and movements per item in one `annotate` doubles the numbers (Ch. 7.5); fix with `Count(..., distinct=True)` or a `Subquery`; the test seeds a case where the naive count is wrong |
| 11 | PROTECT or CASCADE? ✅ | drill | trace | `⚠ HAND-TRACE` models with `CASCADE`, `PROTECT`, `SET_NULL` (Ch. "Try it: PROTECT or CASCADE?"); after 4 deletes write the row counts or `ProtectedError` |
| 12 | Change a model without breaking the team ✅ | applied | explain | what `makemigrations` asks when you add a non-null field with no default, the three safe answers, when a data migration is needed and why migrations are committed and never edited after sharing (Ch. 8.2–8.5) |

## C. Writing data safely (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 13 | One function that changes stock ✅ | applied | code | `move_stock(item, delta, reason, user)` inside `transaction.atomic()`: `F("quantity") + delta`, a `Movement` row, a `CheckConstraint(quantity__gte=0)` that makes overselling raise `IntegrityError`, nothing half-done on failure (Ch. 9.3–9.4, project step 2) |
| 14 | An idempotent import ✅ | deep | code | `import_items(rows)` with `update_or_create` by `sku`; running it twice gives the same database; returns `(created, updated)`; `bulk_create` for a large new batch (Ch. 9.1–9.2) |
| 15 | A custom QuerySet ✅ | applied | code | `ItemQuerySet.low_stock(threshold)`, `.active()`, `.in_category(slug)`; `objects = ItemQuerySet.as_manager()`; chainable in any order (Ch. 9.5) |

## D. The admin, forms and views (Ch. 10–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 16 | An admin worth using ✅ | applied | code | `ItemAdmin` with `list_display`, `search_fields`, `list_filter`, `readonly_fields=("quantity",)`, an action "mark discontinued"; tests as superuser: changelist 200, `?q=` filters, the action changes rows; a staff user with only the view permission gets 403 on change (Ch. 10.2–10.3) |
| 17 | Middleware and a signal ✅ | applied | code | middleware adding `X-Request-ID`; a `post_save` signal that records a `LowStockAlert` when quantity falls below the threshold, once per crossing (Ch. 16.1–16.2) |
| 18 | A ModelForm without mass assignment ✅ | applied | code | `ItemForm(fields=["name", "sku", "price", "category"])`; posting `quantity=999` changes nothing (Ch. "Try it: mass assignment"); `clean_sku` upper-cases and checks the pattern |
| 19 | Show, validate, redirect ✅ | applied | code | a create view with the form: GET shows it, invalid POST re-shows with errors (200), valid POST redirects (302); the test client enforces CSRF |
| 20 | CRUD with generic views ✅ | drill | code | `ListView`, `DetailView`, `CreateView`, `UpdateView` with `success_url = reverse_lazy(...)`; unknown pk → 404 (Ch. 12.1, "Try it: where is the 404?") |

## E. Auth, testing, DRF and the choice (Ch. 13–19)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 21 | 403 or redirect? ✅ | drill | trace | `⚠ HAND-TRACE` 6 requests (anonymous / logged in without permission / with permission) to views with `login_required`, `permission_required(raise_exception=True)`, `LoginRequiredMixin`; write the status and `Location` (Ch. "Try it: 403 or redirect?") |
| 22 | A test that catches the IDOR ✅ | challenge | code | the learner writes `check_owner_only(client_factory)`; the test runs it against a view that checks ownership (must pass) and one that does not (must fail) (Ch. 14, "Try it: which test catches the IDOR?") |
| 23 | An inventory API with DRF ✅ | applied | code | `ItemSerializer` (quantity read-only, `validate_price` > 0), `ItemViewSet` with `IsAuthenticated`, a `DefaultRouter`; anonymous → 403, POST 201, a negative price → 400 with the field error; `GET` list in 1 query (Ch. 15.4, "why is `quantity` ignored?") |
| 24 | Choose a framework and defend it ✅ | deep | explain | `assessment = "explain"`. Outcome. For three of the chapter's seven scenarios (Ch. 19.3) choose Django, Flask or FastAPI using the five questions (Ch. 19.2); `answer.md` gives a model defence and a checklist (admin and ORM needs, async/real time, team, validation, what you give up) |

## F. Project (Ch. 18)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | An admin-driven inventory app ✅ | challenge | code | `assessment = "build"`. `Category`, `Item`, `Movement`; `move_stock` (p013 rules); admin with search, filters and a read-only quantity changed only through movements; a DRF API (`/api/items/`, `POST /api/items/<pk>/move/`); tests: stock never negative, every change has a movement, staff vs anonymous access, API list ≤ 2 queries, admin changelist works |

## Counts check

Tiers: drill 1, 2, 3, 4, 5, 6, 11, 20, 21 (9); applied 7, 8, 9, 12, 13, 15, 16, 17, 18, 19, 23 (11); deep 10, 14, 24 (3); challenge 22, 25 (2). Total 25.
Kinds: trace 2, 3, 8, 11, 21 (5); explain 12, 24 (2); code 18.

## Risks and open questions

- `django.setup()` can run only once per process, and each problem's pytest run is its own process, so one conftest per problem is fine. Do not share a `solution` between Django problems.
- Model changes inside one test run are impossible (tables are built once at import); problems never ask the learner to change a model during a test.
- `check --deploy` (Ch. 17.2) and management commands (Ch. 16.3) have no problem of their own; they are covered in p025's `solution.md` and could replace p017 if the signal problem proves too fiddly.
- DRF's error message wording changes between versions: tests check status codes and which field has an error, not the message text.

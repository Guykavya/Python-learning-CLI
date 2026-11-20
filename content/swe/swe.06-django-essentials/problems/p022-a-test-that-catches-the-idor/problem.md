# A test that catches the IDOR

Chapter section 14.3 and "Try it: which test catches the IDOR?". A security rule needs a test with **two actors**: with only one user, the bug that lets user B read user A's data is invisible.

`solution.py` already contains a `Note` model (an `owner` and a `text`) and **three views** that you must not change:

| URL | What it does |
|---|---|
| `/safe/notes/<pk>/` | correct: `get_object_or_404(Note, pk=pk, owner=request.user)` |
| `/leaky/notes/<pk>/` | has the IDOR bug: any logged-in user can read any note |
| `/closed/notes/<pk>/` | too strict: always 404, even for the owner |

Your job is to write the function

```python
def check_owner_only(client, base):
    ...
```

`client` is a fresh `django.test.Client`; `base` is `"/safe"`, `"/leaky"` or `"/closed"`. Your function must **create** two users and one note owned by the first user, ask for `f"{base}/notes/{note.pk}/"` as each user, and use `assert` statements (with messages) so that it:

- **passes** (raises nothing) when the notes follow the rule: the owner gets 200 and sees the text, and another logged-in user gets **404** and does not see the text;
- **raises `AssertionError`** for a view that breaks the rule, whichever way it breaks it. The tests run your check against all three views: it must pass on `/safe` and fail on `/leaky` and on `/closed`.

Log users in with `client.force_login(user)`; calling it again with another user switches the session.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`; do not change a model while tests run. Each test starts with an empty database, so user names such as `"alice"` are free to use.

## Example

```text
check_owner_only(Client(), "/safe")    -> returns (nothing wrong)
check_owner_only(Client(), "/leaky")   -> AssertionError: another user got 200 for /leaky/notes/1/, expected 404
check_owner_only(Client(), "/closed")  -> AssertionError: the owner got 404 for /closed/notes/1/, expected 200
```

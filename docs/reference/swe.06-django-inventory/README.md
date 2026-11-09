# Reference project for swe.06 (Django essentials)

The finished inventory app from section 18 of the chapter, exactly as the chapter builds it.
Use it to compare with your own work when you are stuck. Try to type the project yourself first.

```bash
cd docs/reference/swe.06-django-inventory
python manage.py migrate
python manage.py test          # 25 tests
python manage.py createsuperuser
python manage.py runserver
```

`sandbox/` holds the three helper files used by the short ORM examples in sections 6, 7, 9, 16
and 17 (`sandbox.py`, `catalog.py`, `shop.py`). Run those examples from inside that folder.
The `SECRET_KEY` in `settings.py` is a throw-away development value, never reuse it.

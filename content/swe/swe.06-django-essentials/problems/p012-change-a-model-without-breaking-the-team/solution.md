## Approach

Think in two parts. First, what the database needs: a value for every existing row, because the column is `NOT NULL`. Second, how the change travels: other people and other servers get it by running the **same migration files**, so those files must be the same everywhere and must not change after they have run.

See `answer.md` for a model answer and a checklist. The key sentences: **Django cannot invent the value for old rows, so you decide it (a real default, `NULL`, or a fill-in step); and a migration is history, so you add to it and never rewrite it.**

Example of the safest flow for "every item gets its own barcode":

```bash
# 1. models.py: barcode = models.CharField(max_length=13, null=True, blank=True)
python manage.py makemigrations inventory            # 0004_item_barcode
# 2. fill the values
python manage.py makemigrations inventory --empty --name fill_barcodes     # 0005, write RunPython
# 3. models.py: barcode = models.CharField(max_length=13)   (required)
python manage.py makemigrations inventory            # 0006: AlterField; Django may ask about NULL rows: none are left
python manage.py migrate
git add inventory/migrations && git commit
```

Check the real command text in section 8 of the chapter and in the reference project `docs/reference/swe.06-django-inventory/` (its migrations folder shows a real `AddField` and a data migration).

## Complexity

Not applicable. (On a table with millions of rows the cost of `AddField` and of the backfill matters: backfill in batches, and read the SQL with `sqlmigrate`.)

## Another way

Make the barcode a separate model (`Barcode` with a `OneToOneField` to `Item`). Then adding it needs no value for old rows: items simply have no barcode row yet. This is also a good answer when "no barcode" is a normal state and not a gap in your data.

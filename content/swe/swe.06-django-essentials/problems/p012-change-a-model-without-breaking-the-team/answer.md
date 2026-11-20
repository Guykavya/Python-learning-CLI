## Model answer

**1. The question.** The new column is `NOT NULL`, but the 1,000 existing rows have no value for it. Django cannot invent one: should it be `""`, `0`, or something else? So `makemigrations` (in interactive mode) says that the field is non-nullable with no default, and offers (1) to provide a **one-off default** now, or (2) to quit and fix `models.py`. With `--noinput` it refuses. Django only writes the migration once every old row has a defined value.

**2. Three safe ways.**
- **A real default in the model:** `barcode = models.CharField(max_length=13, blank=True, default="")`. Old rows get `""`, new rows can be created without it, and the meaning "no barcode yet" is clear. For text fields the convention is `""`, not `NULL`.
- **`null=True, blank=True`:** old rows get `NULL`, "unknown" is stored honestly. Fill the real values later, then (optionally) make the field required in a later migration.
- **Three steps for a field that must become required** (and for big tables that stay online): migration 1 adds the field as nullable, migration 2 is a **data migration** that fills it, migration 3 makes it `NOT NULL`.

The quick one-off default (`''` typed at the prompt) puts the same fake value in all 1,000 rows. It is fine when one value really fits all of them (a status `"active"`), wrong when each row needs its own barcode: you now have 1,000 identical, meaningless barcodes that look valid.

**3. Data migration.** You need one when the **data** must change with the schema: here, computing or importing the real barcode of each of the 1,000 items. Create an empty migration (`makemigrations --empty --name fill_barcodes`) and add `migrations.RunPython(forward, backward)`. Two rules: get the model with `apps.get_model("inventory", "Item")` (the **historical model** as it was at that point), never `from inventory.models import Item`, because today's model may not match the table at that step; and give a **reverse function** (`RunPython.noop` if there is nothing to undo), or going backwards raises `IrreversibleError`.

**4. Team rules.** Migration files are part of the code: **commit** them, so every developer, the test server and production build the same tables from the same history. Once another database has applied a migration, never edit or delete it: their record of what ran would no longer match the file. Write a **new** migration that fixes the problem. If two branches both create `0004`, merge them (`makemigrations --merge`) and test on a fresh database. Run `migrate` as its own deployment step, and check CI with `makemigrations --check`.

**Checklist: your answer should mention**
- [ ] the new field is `NOT NULL` with no default, and the 1,000 existing rows need a value, so Django asks (one-off default, or quit and edit the model)
- [ ] option: a real `default` in the model (for text: `blank=True, default=""`)
- [ ] option: `null=True` (and `blank=True`), fill the values later
- [ ] option: three steps: add as nullable, fill with a data migration, then make it required (safe on big tables)
- [ ] a one-off default gives every old row the same fake value, which is wrong when each row needs its own
- [ ] a data migration is needed when existing data must be computed or changed together with the schema (`RunPython`)
- [ ] inside `RunPython`: use `apps.get_model(...)` (the historical model), never import the real model
- [ ] give a reverse function (`RunPython.noop`) so the migration can be undone
- [ ] migration files are committed with the code; never edit or delete a migration that others have applied, write a new one instead

## Hint 1

Picture the table before the change: 1,000 rows and no column called `barcode`. After the change every row must have a value in that column, and the column does not allow `NULL`. What does Django not know that only you know? Why do you think it asks instead of guessing?

## Hint 2

Think of the options on the field itself (`default=`, `null=True`) and of the order of work for a field that must end up required. For the second half, ask: if I edit a migration after a colleague has already run it, what do his database and the file say about each other? And what does a `RunPython` function receive instead of the real model class?

## Hint 3

```text
1. NOT NULL + no default + 1,000 rows -> Django asks: one-off default, or quit
2. real default / null=True / three steps (nullable -> data migration -> NOT NULL); one-off '' = 1,000 identical fake barcodes
3. data migration: RunPython(forward, noop-or-reverse), apps.get_model(), never import models
4. commit migrations; never edit a shared one; new migration instead
```

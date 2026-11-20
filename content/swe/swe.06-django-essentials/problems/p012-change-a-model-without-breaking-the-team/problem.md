# Change a model without breaking the team

Chapter sections 8.2 to 8.5 and "Try it: the missing default". The inventory app is live. The table `Item` has 1,000 rows. Your team lead asks you to add a **barcode** to every item:

```python
barcode = models.CharField(max_length=13)      # no default, not null
```

You run `python manage.py makemigrations`. Django stops and asks a question instead of writing the file.

In `answer.md` write a clear explanation (about 150 to 300 words) that covers:

1. **What does `makemigrations` ask, and why can it not decide alone?** (Think about the 1,000 existing rows.)
2. **Three safe ways to answer or to change the model**, and when each one fits. Say what is wrong with typing a one-off default such as `''` when every item needs a *different* real barcode.
3. **When do you need a data migration**, and the two rules for writing the `RunPython` function (how to get the model, and what to give for going backwards).
4. **Why migration files are committed to git and never edited after other people have applied them.** Say what you do instead when you discover a mistake in a migration that is already shared.

A good answer uses the words *migration*, *default*, *null*, *data migration*, *historical model*, *commit*.

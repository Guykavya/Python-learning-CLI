## Hint 1

A relative import like `from . import helpers` asks: "which package am I in?" Python answers with
`__package__`. What is `__package__` when you run `python app/main.py`? Can `.` mean anything then?

## Hint 2

Command 1: no package, so the relative import raises `ImportError`. The `except` block does a plain
`import helpers`. Which folder is `sys.path[0]`, and does it contain `helpers.py`? What is the name of
the module it creates?

Command 2: `-m app.main` imports `app` first (its `__init__.py` prints), then runs `main.py` as
`__main__`. Now `.` means `app`, so `helpers` is loaded as `app.helpers`. Note the order: the line
`helpers loaded as ...` is printed while the import runs, before `relative import worked`.

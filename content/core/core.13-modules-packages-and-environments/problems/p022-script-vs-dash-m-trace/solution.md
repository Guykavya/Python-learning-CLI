## Approach

**Command 1, `python app/main.py`.** Python treats the file as a plain script. `__name__` is
`"__main__"` and `__package__` is `None`, so `repr` shows `None`. `from . import helpers` needs a
parent package and there is none, so it raises
`ImportError: attempted relative import with no known parent package`. The `except` block runs
`import helpers`. `sys.path[0]` is the folder `app/`, so `helpers.py` is found there and loaded as a
top-level module named `helpers`. The package `app` is never imported, so `app package loaded` is
never printed.

**Command 2, `python -m app.main`.** Python imports the package `app` first (prints
`app package loaded`), then runs `app/main.py` as `__main__` with `__package__ = 'app'`.
The relative import now means `app.helpers`. Loading it prints `helpers loaded as app.helpers`, and
only then `relative import worked`.

## Output

```text
main: __name__ = __main__
main: __package__ = None
ImportError: attempted relative import with no known parent package
helpers loaded as helpers
HI! from helpers
app package loaded
main: __name__ = __main__
main: __package__ = 'app'
helpers loaded as app.helpers
relative import worked
HI! from app.helpers
```

## Complexity

Not applicable.

## Another way

The `try/except` fallback "works" but is a trap: in command 1 the same file could be imported twice
under two names (`helpers` and `app.helpers`) in a bigger program. The clean rule is: files inside a
package are run with `python -m pkg.module` from the folder above the package, and they use relative
(or full `app.helpers`) imports only.

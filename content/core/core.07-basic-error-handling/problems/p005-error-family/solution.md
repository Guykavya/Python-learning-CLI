## Approach

`except Parent` catches every subclass of `Parent`, so four clauses naming the four parent
classes cover every case in the table. None of the four families overlap, so their order does not
matter here. Anything else matches no clause and propagates by itself.

## Code

```python
def error_family(func, *args):
    """Call func(*args) and return 'ok', 'lookup', 'arithmetic', 'value' or 'type'."""
    try:
        func(*args)
    except LookupError:
        return "lookup"
    except ArithmeticError:
        return "arithmetic"
    except ValueError:
        return "value"
    except TypeError:
        return "type"
    return "ok"
```

## Complexity

O(1) plus whatever `func` costs.

## Another way

One clause `except (LookupError, ArithmeticError, ValueError, TypeError) as e:` followed by
`isinstance` tests on `e` also works, but four clauses say the same thing more directly.

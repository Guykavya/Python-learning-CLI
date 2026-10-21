## Approach

Everything before `/` is positional-only; everything after `*` is keyword-only. Python's argument
binding enforces both rules and raises `TypeError` for calls that break them, so the body only
needs the arithmetic.

## Code

```python
def power(base, exp, /, *, modulo=None):
    """Return base ** exp, reduced modulo `modulo` when it is given."""
    if modulo is None:
        return base ** exp
    return pow(base, exp, modulo)
```

## Complexity

`base ** exp` is O(size of the result) in practice; `pow` with a modulus keeps numbers small, O(log exp) multiplications.

## Another way

Without `/`, a caller who writes `power(base=2, exp=3)` ties you to those names forever. With it
you may rename them freely. That is why many built-ins, like `pow` itself, are positional-only.

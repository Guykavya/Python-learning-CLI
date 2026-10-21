## Approach

`type(x)` returns the class of the object `x` refers to. Printing it shows
`<class 'name'>`.

## Code

```python
print(type(count))
print(type(price))
print(type(label))
print(type(is_ready))
print(type(nothing))
```

## Why each answer

- `42` has no decimal point: `int`.
- `99.5` has a decimal point: `float`.
- `"42"` is in quotes: `str`. Looks do not matter; quotes do.
- `True` (capital T) is a `bool`.
- `None` is the single object of type `NoneType`. It means "no value".

## Another way

`print(type(count).__name__)` prints just `int`. The task wants the full
`<class '...'>` form.

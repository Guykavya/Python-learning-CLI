## Approach

The area is `width * height`. `return` hands that value back to the caller. The docstring is a
triple-quoted string that is the first statement of the body; Python stores it in
`rectangle_area.__doc__`, which is what `help()` and editors show.

## Code

```python
def rectangle_area(width, height):
    """Return the area of a width x height rectangle."""
    return width * height
```

## Complexity

O(1): one multiplication.

## Another way

You could compute into a name first, `area = width * height` then `return area`. It is the
same function, a line longer. Either way, the summary line of the docstring should start with a
verb ("Return ...") and end with a full stop, as PEP 257 recommends.

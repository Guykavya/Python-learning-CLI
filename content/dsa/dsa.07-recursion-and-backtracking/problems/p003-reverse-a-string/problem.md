# Reverse a string, recursively

Write `reverse(s)` that returns the string `s` backwards, using recursion.
Not allowed: slicing with a negative step (`s[::-1]`), `reversed`, and loops (`for`, `while`, comprehensions). Ordinary slices such as `s[1:]` are fine.

## Example

```python
>>> reverse("abc")
'cba'
>>> reverse("")
''
>>> reverse("naïve")
'evïan'
```

## Constraints

- `0 <= len(s) <= 500`

## Think about

The reverse of `"abc"` is the reverse of `"bc"` followed by `"a"`. What is the reverse of a string with 0 or 1 characters?

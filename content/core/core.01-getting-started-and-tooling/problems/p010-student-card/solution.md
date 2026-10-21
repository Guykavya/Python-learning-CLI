## Approach

Read the three lines in order. Build the border once. Join each label with its
value using `+`, which adds no extra spaces.

## Code

```python
name = input()
course = input()
year = input()

border = "+" + "-" * 20 + "+"
print(border)
print("Name   : " + name)
print("Course : " + course)
print("Year   : " + year)
print(border)
```

## Why `+` works for the year

`input()` always returns a `str`, even for `2`. So `"Year   : " + year` joins two
strings. If you had converted it with `int()`, `+` would fail with `TypeError`.

## Another way

`print("Name   :", name)` also works, because `print` puts one space between
its two values. Then the label must not include the trailing space.

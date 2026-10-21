# Wrap a paragraph

Read a width (a whole number, at least 10) and then a paragraph on one line. Print:

1. the paragraph wrapped so no line is longer than the width (`textwrap.fill`),
2. a line of `-` characters exactly `width` long,
3. a one-line preview that fits in the width, ending in ` ...` if it had to be shortened (`textwrap.shorten` with `placeholder=" ..."`).

**Example**

Input:
```
20
Strings are immutable sequences of Unicode code points.
```
Output:
```
Strings are
immutable sequences
of Unicode code
points.
--------------------
Strings are ...
```

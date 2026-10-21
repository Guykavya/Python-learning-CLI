# Pad a code

Read a code typed as text (for example an order number). Print three lines:

1. The code padded with zeros on the left to width 6, using `zfill`.
2. The code right-aligned in width 8 with dots on the left.
3. The code left-aligned in width 8 with dots on the right, followed by `|`.

**Example**

Input:
```
42
```
Output:
```
000042
......42
42......|
```

If the code is already wider than the width, it is printed unchanged (padding never cuts). A minus sign stays in front with `zfill`: `-42` becomes `-00042`.

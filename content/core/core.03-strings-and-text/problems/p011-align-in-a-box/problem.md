# Align with f-strings

Read a word, then a width (a whole number). Print four lines, each wrapped in square brackets:

1. the word left-aligned in the width
2. the word right-aligned in the width
3. the word centred in the width
4. the word centred in the width with `*` as the fill

**Example**

Input:
```
cat
9
```
Output:
```
[cat      ]
[      cat]
[   cat   ]
[***cat***]
```

Use f-strings with a **nested field** for the width, like `{word:<{width}}`. When the padding cannot be split evenly, f-strings put the extra space on the right; that is what the tests expect.

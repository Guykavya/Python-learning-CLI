# Align two lines into columns

Read two lines of words. Print them again so that the words line up in columns.

- Column `k` holds word `k` of each line. Its width is the length of the **longer** of the
  two words.
- A word made only of digits is **right-aligned** in its column. Any other word is
  **left-aligned**.
- Columns are separated by **two spaces**. Lines must not end with spaces.
- If the two lines have a different number of words, print only
  `Lines have different word counts`.

**Example**

Input:
```
item qty price
notebook 3 45
```
Output:
```
item      qty  price
notebook    3     45
```

Column widths are 8, 3 and 5. `3` and `45` are right-aligned; the other words are
left-aligned.

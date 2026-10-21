# Count a letter

Read a line of text, then a single letter on the next line. Print two lines:

```
Exact: <how many times the letter appears, case-sensitive>
Any case: <how many times it appears, ignoring case>
```

**Example**

Input:
```
Banana Bread
b
```
Output:
```
Exact: 0
Any case: 2
```

For "any case", compare with `casefold()`, which is meant for case-insensitive matching.

# Draw a title banner

Read a title and a width `W` (a whole number, at least 10). Print a three-line banner exactly `W` characters wide:

```
+--------------------+
|   Strings & Text   |
+--------------------+
```

Rules:

- Top and bottom: `+`, then `W - 2` dashes, then `+`.
- Middle: `| `, the title centred in `W - 4` characters, then ` |`. When the padding is uneven, the extra space goes on the **right** (this is how the f-string `^` alignment works).
- The title first has its whitespace collapsed. If it does not fit in `W - 4` characters, shorten it at a word boundary and end it with `...`. Use `textwrap.shorten(title, width=W - 4, placeholder="...")`, which does both jobs and leaves short titles alone.

**Example**

Input:
```
Strings & Text
22
```
Output:
```
+--------------------+
|   Strings & Text   |
+--------------------+
```

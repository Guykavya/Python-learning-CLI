# Tidy the spaces

Users often type extra spaces. Read one line and print two lines, each wrapped in square brackets so the spaces are visible:

1. The line with spaces and tabs removed from **both ends** only.
2. The line with every run of whitespace replaced by a **single space**, and nothing at either end.

**Example**

Input (dots show spaces here; the real input has spaces):
```
···Hello····big···world··
```
Output:
```
[Hello····big···world]
[Hello big world]
```

(Again, the dots in the first output line are really spaces.)

A line containing only spaces gives `[]` twice.

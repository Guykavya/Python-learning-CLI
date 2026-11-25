## Hint 1

Which function gives the number of rows of a frame? There are three cases: equal, more, fewer. Which should return, and which
should raise? Why do the two raising cases deserve different words?

## Hint 2

```text
n_before = rows of before;  n_after = rows of after
if n_after > n_before: raise AssertionError("fan-out in <label>: <n_before> → <n_after> rows")
if n_after < n_before: raise AssertionError("rows lost in <label>: ... ")
return after
```

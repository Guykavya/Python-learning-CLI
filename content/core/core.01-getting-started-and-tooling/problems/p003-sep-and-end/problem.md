# Dates with sep and end

`starter.py` defines three variables:

```python
day = 18
month = 10
year = 2026
```

Print exactly two lines:

```
18/10/2026
Loading...done
```

Rules (the tests check them):

1. Line 1 comes from **one** `print` call that receives `day`, `month` and
   `year` as three separate values and uses the `sep` argument.
2. Line 2 comes from **two** `print` calls. The first prints `Loading...` and
   uses the `end` argument so the second, which prints `done`, continues on the
   same line.

**Example**

Output:
```
18/10/2026
Loading...done
```

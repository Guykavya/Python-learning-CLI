## Hint 1

Write the eight numbers in a row and add them up in two steps: first with the two codes, then without. How many values
does `mean` divide by in each case? For the median, sort the numbers first: which position (or which two) is in the
middle for eight values, and for six?

## Hint 2

```text
age = 25 31 -1 40 999 30 35 33     sum = ?   n = 8   mean = sum / 8
sorted: -1 25 30 31 33 35 40 999   median = average of the 4th and 5th
clean: the two codes become NaN -> 6 numbers, 2 missing
mean of the 6 = their sum / 6;   median of the 6 = average of the 3rd and 4th when sorted
the list: NaN forces floats -> 25.0
```

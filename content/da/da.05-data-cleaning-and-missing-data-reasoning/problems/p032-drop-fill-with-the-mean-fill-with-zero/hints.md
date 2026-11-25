## Hint 1

Which five values are present, what are their sum, mean and squared distances from the mean? What does each treatment
put in the three empty places? For each treatment, how many values and what mean and sum of squares does the Series have?

## Hint 2

```text
observed: 4, 8, 6, 10, 2 -> sum 30, mean 6; squared distances 4, 4, 0, 16, 16 -> sum 40
dropna: n = 5, std = sqrt(40 / 4)
fill with the mean 6: n = 8, the three new values add 0 to the sum of squares -> sqrt(40 / 7)
fill with 0: n = 8, sum 30 -> mean 30 / 8; sum of squares around that mean, divided by 7, then the root
last line: count() of non-missing, len of all
```

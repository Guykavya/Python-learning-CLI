## Hint 1

Work one example on paper first: 20,000 users, 4 writes each per day. How many writes a day? How many seconds in a day? So how many writes per second on average? Then reads are a multiple of writes. Which numbers are rounded for display, and when must the rounding happen so that it does not spoil the others?

## Hint 2

```text
avg_write = dau * writes_per_user / 86_400          (keep it unrounded)
avg_read  = avg_write * reads_per_write
storage_gb = dau * writes_per_user * 365 * years * bytes_per_item / 1e9
return the five values, rounded (2, 2, 2, 2 and 1 decimals) only now
```

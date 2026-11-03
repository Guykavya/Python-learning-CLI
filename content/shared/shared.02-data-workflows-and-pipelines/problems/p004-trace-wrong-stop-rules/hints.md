## Hint 1

First work out `get_page` for both lists on paper: for each page number, what are `start`,
the slice `ORDERS[start:start + 3]`, and `next_page`? Then walk each loop one request at a
time, writing down the page number it asks for and what it adds. What is `(0 - 1) * 3`, and
what does a slice like `ORDERS[-3:0]` give?

## Hint 2

```
seven orders: page 1 -> [101,102,103] next 2 | page 2 -> [104,105,106] next 3 | page 3 -> [107] next None
six orders:   page 1 -> [101,102,103] next 2 | page 2 -> [104,105,106] next None | page 3 -> [] next None
page 0: start = -3, ORDERS[-3:0] -> stop index 0 comes before start -> []
len(ORDERS) // 3 is floor division: 7 // 3 == 2
skips_first_page: page 1's data is fetched but never added (got += happens only inside the loop)
```

## Approach

Build the page table for each list first, then run each loop against it.

| `ORDERS` | page 1 | page 2 | page 3 |
|---|---|---|---|
| seven (101..107) | `[101, 102, 103]`, next 2 | `[104, 105, 106]`, next 3 | `[107]`, next None |
| six (101..106) | `[101, 102, 103]`, next 2 | `[104, 105, 106]`, next None | `[]`, next None |

| Call | What happens | Output |
|---|---|---|
| `short_page_stops`, seven | pages 1 and 2 are full, page 3 has 1 order (< 3) so it breaks | `[1, 2, 3]`, all 7 |
| `short_page_stops`, six | page 2 is full, so it asks for page 3 too, which is empty (0 < 3) | `[1, 2, 3]`, all 6, but **one wasted request** |
| `count_pages_first`, seven | `7 // 3 == 2`, so `range(1, 3)` | `[1, 2]`, **107 is lost** |
| `count_pages_first`, six | `6 // 3 == 2` happens to be right | `[1, 2]`, all 6 |
| `skips_first_page`, seven | page 1 is fetched before the loop, but `got +=` only runs inside the loop for pages 2 and 3 | `[1, 2, 3]`, **101 to 103 lost** |
| `starts_at_zero`, seven | page 0: `start = -3`, `ORDERS[-3:0]` is empty (the stop 0 is before the start), so it stops at once | `[0]`, `[]` |
| `follows_next_page`, six | page 2 says `next_page` None | `[1, 2]`, all 6 |

## Full output

```
short_page_stops [1, 2, 3] [101, 102, 103, 104, 105, 106, 107]
short_page_stops [1, 2, 3] [101, 102, 103, 104, 105, 106]
count_pages_first [1, 2] [101, 102, 103, 104, 105, 106]
count_pages_first [1, 2] [101, 102, 103, 104, 105, 106]
skips_first_page [1, 2, 3] [104, 105, 106, 107]
starts_at_zero [0] []
follows_next_page [1, 2] [101, 102, 103, 104, 105, 106]
```

Notice that three of the four buggy loops give the right answer on *one* of the lists. That
is why pagination tests need several data sizes: one that ends on a full page, one that ends
on a short page, and one that is empty.

## Complexity

`follows_next_page` makes exactly one request per page. `short_page_stops` makes one extra
request whenever the data size is a multiple of the page size.

## Another way

`count_pages_first` can be "fixed" with ceiling division, `range(1, (n + per_page - 1) // per_page + 1)`,
but only if the API tells you the total count *and* the count does not change while you read.
Following `next_page` needs neither.

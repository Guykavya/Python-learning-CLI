## Hint 1

Going downwards, the bottom row is where you stop, and you would have to take the minimum over the whole last row, with edge cases for the first and last cell of each row. Go the other way. Let `g[i][j]` = the cheapest path from `(i, j)` **down to the bottom**. What is `g` on the bottom row?

## Hint 2

`g[i][j] = triangle[i][j] + min(g[i+1][j], g[i+1][j+1])`. Both children always exist (the row below is one longer), so there are no edge cases. The answer is `g[0][0]`. You only ever read the row just below, so keep one list `below` and replace it row by row.

## Hint 3

```
below = copy of the last row
for i from n-2 down to 0:
    below = [triangle[i][j] + min(below[j], below[j+1]) for j in 0..i]
return below[0]
```

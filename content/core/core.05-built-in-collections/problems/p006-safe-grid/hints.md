## Hint 1

How many separate row lists do you need? How do you make sure each row is a new list?

## Hint 2

`[["."] * cols] * rows` makes **one** row and repeats references to it. Use a comprehension:
`[["."] * cols for _ in range(rows)]`.

## Hint 3

For each position: `grid[r][c] = "#"`. Print each row with `"".join(row)`.

## Hint 1

Where does each chunk start? List the start positions for the example.

## Hint 2

`range(0, len(items), k)` gives the starts 0, 3, 6. A chunk is `items[start:start + k]`.

## Hint 3

`chunks = [items[s:s + k] for s in range(0, len(items), k)]`. The last slice is cut short
automatically.

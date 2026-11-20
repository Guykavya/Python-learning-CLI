## Hint 1

`f[mask][last]` = the shortest time of a path that starts at 0, visits exactly the places in `mask` (bit `i` set = place `i` visited), and is now standing at `last`. The past order does not matter for the future: only the set of visited places and where you stand. That is why `2**n * n` states replace `(n - 1)!` orders.

## Hint 2

Base: `f[1][0] = 0` (only place 0 visited, standing there). For each `mask` in increasing order and each `last` with a finite `f[mask][last]`, try every unvisited `nxt`:
`f[mask | 1 << nxt][nxt] = min(..., f[mask][last] + dist[last][nxt])`. Store `parent[new_mask][nxt] = last` whenever it improves. Adding a bit makes `mask` bigger, so every state is final before the loop reaches it.

## Hint 3

```
full = (1 << n) - 1
length, last = min over last in 1..n-1 of (f[full][last] + dist[last][0], last)
order = []; mask = full
while last is not None:            # walk the parents back to place 0
    order.append(last)
    prev = parent[mask][last]
    mask = mask without bit last
    last = prev
order.reverse()                    # now it starts with 0
```

Handle `n == 1` separately: `(0, [0])`.

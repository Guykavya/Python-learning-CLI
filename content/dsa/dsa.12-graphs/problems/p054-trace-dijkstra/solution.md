## Approach

Keep the heap as a set of pairs and the `dist` list on paper; at each pop decide stale or not, then relax the neighbours in adjacency order.

## Expected output

```text
pop (0, 0): heap [(2, 2), (7, 1)]  dist [0, 7, 2, '-', '-']
pop (2, 2): heap [(5, 1), (7, 1), (10, 3), (11, 4)]  dist [0, 5, 2, 10, 11]
pop (5, 1): heap [(6, 3), (7, 1), (10, 3), (11, 4)]  dist [0, 5, 2, 6, 11]
pop (6, 3): heap [(7, 1), (8, 4), (10, 3), (11, 4)]  dist [0, 5, 2, 6, 8]
pop (7, 1): stale, skip
pop (8, 4): heap [(10, 3), (11, 4)]  dist [0, 5, 2, 6, 8]
pop (10, 3): stale, skip
pop (11, 4): stale, skip
[0, 5, 2, 6, 8]
```


## Why

| pop | stale? | relaxations (new pushes) | heap after |
|---|---|---|---|
| `(0, 0)` | no | 1: 7, 2: 2 | `(2,2) (7,1)` |
| `(2, 2)` | no | 1: 2+3 = 5 (beats 7), 3: 2+8 = 10, 4: 2+9 = 11; to 0: 4 is not < 0 | `(5,1) (7,1) (10,3) (11,4)` |
| `(5, 1)` | no | 3: 5+1 = 6 (beats 10); to 0: 12, to 2: 8, no | `(6,3) (7,1) (10,3) (11,4)` |
| `(6, 3)` | no | 4: 6+2 = 8 (beats 11); to 1: 7, to 2: 14, no | `(7,1) (8,4) (10,3) (11,4)` |
| `(7, 1)` | yes, 7 > 5 | | |
| `(8, 4)` | no | to 3: 10, to 2: 17, no | `(10,3) (11,4)` |
| `(10, 3)` | yes, 10 > 6 | | |
| `(11, 4)` | yes, 11 > 8 | | |

Vertex 1 dropped from 7 to 5 (through 2); vertex 3 dropped from 10 to 6 (through 1); vertex 4 dropped from 11 to 8 (through 3). Seven pairs were pushed and three were stale. The edge `2 - 4` gave the first, worse distance of 4; the final shortest route to 4 is `0 2 1 3 4` (`2 + 3 + 1 + 2 = 8`), which does not use it.

## Another way

Check the final line without the heap: the shortest routes from 0 are `0 -> 2` (2), `0 -> 2 -> 1` (5), `0 -> 2 -> 1 -> 3` (6), `0 -> 2 -> 1 -> 3 -> 4` (8). Then the order of the normal pops must be the vertices sorted by these distances: 0, 2, 1, 3, 4.

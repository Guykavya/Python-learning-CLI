## Hint 1

Split the problem: (a) turn the header into a list of `(range, q)`; (b) for one offered type, find its q; (c) pick the best offered type.

## Hint 2

For (b), look at every range that matches the offered type, and keep the q of the most **specific** one. Give each match a score: exact 3, `type/*` 2, `*/*` 1. A less specific range with a higher q must **not** win over a more specific one with q=0.

## Hint 3

```text
ranges = [(media_lowercase, q)] from splitting on "," then ";"
for each offered type (in server order):
    best_score = 0; q_of_best = 0
    for each range that matches: if score > best_score: best_score, q_of_best = score, q
    if q_of_best > best_q so far: choose it       # strictly greater keeps the server's order on ties
```

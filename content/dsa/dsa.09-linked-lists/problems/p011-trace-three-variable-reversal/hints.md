## Hint 1

Step 1 starts with `prev = None`, `cur = 1`. `nxt = cur.next` is node `2`. Then node `1` is pointed at `None`, `prev` becomes `1` and `cur` becomes `nxt`, which is `2`. The reversed part is just `1`. Write that line, then repeat with `cur = 2`.

## Hint 2

The print happens **after** `cur = nxt`, so `cur` and `nxt` always name the same node in the printed line. The loop stops after the step in which `cur` becomes `None`. The variable `head` was never changed, so it is still node `1`: what does node `1` point to now?

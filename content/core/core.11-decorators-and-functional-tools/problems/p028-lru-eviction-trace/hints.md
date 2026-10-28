## Hint 1

Keep a small list of what is in the cache, ordered from "used longest ago" to "used just now".
A hit moves its entry to the "just now" end. A miss adds a new entry at that end, and if there
are now three entries, the one at the "longest ago" end is removed.

## Hint 2

Before `square(4)`, the order is `[3, 2]` (2 was just read). So who is thrown out when 4 comes
in? After `cache_clear()` everything is empty and the counters go back to 0. Is `square(n=4)`
the same key as `square(4)`?

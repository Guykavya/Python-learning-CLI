## Hint 1

For each situation ask: how many **real parts** must work together for the thing you want to
know? One function, a few parts, or the whole product?

## Hint 2

Ask a second question: what in the situation is slow, risky or outside your control (money,
network, a browser)? That is what you fake in a unit or integration test.

```
one function, nothing outside        -> unit
a few parts + disk / parser / writer -> integration (tmp_path, no network)
user journey through the real system -> end-to-end (few, slow)
real third-party service             -> separate, rarely-run integration/contract test
```

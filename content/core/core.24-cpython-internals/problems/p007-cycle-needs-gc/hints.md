## Hint 1

After `del a`, does anything still point at the first node? After `del b`, who points at each
node now, and is any of those references reachable from `main`'s variables? Reference counting
frees an object only when its count reaches zero. When does the collector run in this program?

## Hint 2

Track a small table of "who points at whom":

```
before any del:   a -> A, b -> B, A.partner -> B, B.partner -> A
del a:            A still has 1 reference (B.partner)       -> alive
del b:            A and B point only at each other          -> alive, unreachable
gc.collect():     finds the unreachable pair, frees both    -> 2 callbacks, then print
c with no cycle:  del c drops the count to 0                -> freed at once
```

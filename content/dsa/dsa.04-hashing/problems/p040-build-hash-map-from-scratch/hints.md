## Hint 1

Start with the data: a list of `m` empty lists. What does `put` do when the key is already in the chain, and when it is new?

## Hint 2

Write helpers first: `find(key)` returns the position in the chain or -1; then `put`, `get`, `del` use it. Resize by collecting all `(key, value)` pairs and re-inserting them into a fresh table.

## Hint 3

```
m = 8; table = [[] for _ in range(m)]; size = 0
put: chain = table[k % m]; search; update or append; size += 1; if size*4 > m*3: rehash
rehash: pairs = all chain items in order; m *= 2; table = new; append each pair to table[key % m]
```

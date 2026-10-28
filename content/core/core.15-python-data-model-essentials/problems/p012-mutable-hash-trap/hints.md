## Hint 1

Write down what the set stored when `add` ran: the object and the hash of `"a"`. Then follow each later check by asking what hash is computed *now* and whether the stored hash matches.

## Hint 2

```
add(t):   stored hash = hash("a"), stored object = t
t.name = "b"      -> hash("a") is still what the set remembers
t in s            -> computes hash("b"): different bucket/hash -> False
Tag("a") in s     -> hash("a") matches, then == compares with t (name is "b") -> False
for x in s        -> walks stored objects, no lookup
```

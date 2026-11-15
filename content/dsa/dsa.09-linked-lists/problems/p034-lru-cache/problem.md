# LRU cache

A cache keeps at most `capacity` key-value pairs. When it is full and a new key arrives, it throws out the **least recently used** key (LRU). Implement `LRUCache(capacity)` with:

- `get(key)`: the value for `key`, or `-1` if it is not in the cache. A successful `get` makes `key` the **most** recently used.
- `put(key, value)`: insert or update. The key becomes the most recently used. If a new key makes the cache hold more than `capacity` keys, remove the least recently used key first.

Both operations must be **`O(1)`** (chapter section 12). Combine:

- a **dictionary** `key -> node`, to find a key's node in `O(1)`;
- a **doubly linked list** with two sentinels, ordered from most to least recently used, to move a node to the front and to find and remove the last one in `O(1)`. Each node stores its **key** too, so the evicted node can be deleted from the dictionary.

Do not use `collections.OrderedDict` (that is the model the tests compare you with).

## Example (capacity 3)

```text
put a 1
put b 2
put c 3
get a -> 1
put d 4
get b -> -1
put c 30
put e 5
get a -> -1
get c -> 30
get d -> 4
get e -> 5
```

`put d 4` found the cache full (`a`, `b`, `c`). `a` had just been used by `get a`, so the least recently used key was `b`, and `b` was evicted. `put c 30` updated `c` (no eviction) and made it the most recent. `put e 5` then evicted `a`.

## Constraints

- `1 <= capacity <= 10**4`; keys and values are any hashable values / any values. The tests run 200,000 operations on a cache of capacity 10,000 with a time limit, and 5,000 random operations against an `OrderedDict` model.

## Think about

Which operations must touch the linked list? Why does a singly linked list not work here (what does removing a node from the middle need)?

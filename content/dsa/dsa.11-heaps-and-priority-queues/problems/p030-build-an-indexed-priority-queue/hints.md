## Hint 1

Write the plain heap first, without any index: two parallel lists `keys` and `prios` (or one list of pairs), `sift_up` and `sift_down` as in chapter section 3, and `push` and `pop_min`. Let `push` and `pop_min` pass a few tests. Then ask: if I know the **position** of a key, can I change its priority? Where does the position come from?

## Hint 2

Add a dictionary `pos` from key to its position in the lists. The position changes **only when two items are swapped**, so put the updating of `pos` in one function, `_swap(i, j)`, and let every other part of the heap move items only through `_swap`. Also update `pos` when a key is added (its position is the end of the list) and deleted.

With `pos`:

- `update(key, p)`: `i = pos[key]`, set the priority, then restore the heap at `i`: if the item is now smaller than its **parent**, `sift_up(i)`, otherwise `sift_down(i)`.
- `remove(key)`: swap the item with the **last** item, cut the last position off, delete the key from `pos`, then restore the heap at the position `i` where the former last item now stands: it can be too small (move up) **or** too big (move down) for its new place.

## Hint 3

```
swap(i, j):   swap keys[i], keys[j] and prios[i], prios[j];  pos[keys[i]] = i;  pos[keys[j]] = j

restore(i):                       # the item at i may be out of place in either direction
    if i > 0 and prios[i] < prios[parent(i)]: sift_up(i)
    else: sift_down(i)

remove_at(i):
    last = len(keys) - 1
    if i != last: swap(i, last)
    key = keys.pop(); prios.pop(); del pos[key]
    if i != last: restore(i)

pop_min():  item = (keys[0], prios[0]); remove_at(0); return item
update(key, p): i = pos[key]; prios[i] = p; restore(i)
```

Run the example of the statement by hand once, writing `keys` and `pos` after every call.

## Approach

Keep the list on paper with the top on the right. `push n` appends `n`; `pop` removes the rightmost item and prints it with the list that remains.

## Expected output

```text
push 4 [4]
push 7 [4, 7]
pop 7 [4]
push 1 [4, 1]
push 9 [4, 1, 9]
pop 9 [4, 1]
pop 1 [4]
push 5 [4, 5]
top 5 size 2
```

## Why

The two pops after `push 9` remove `9` and then `1`: the newest items leave first (last in, first out). The `4` pushed at the very start is never removed, because something newer is always on top of it when a pop comes. Five values were pushed, three were popped, two remain: `[4, 5]`, with `5` on top.

## Approach

Do the two insertions on paper, then connect the **shape** to the **height**, and the height to the cost of every operation: they all walk one path from the root.

## Model answer

See `answer.md`.

## What to check

- You described both trees, with the right heights (5 and 3).
- You said why sorted input gives a chain (each key is larger than all the earlier ones).
- You tied the cost to the height: `O(h)`, which is `O(n)` for a chain.
- You noticed that the inorder list is the same for every order.
- You named the middle-first order for the smallest height, and balanced trees as the fix.

## Another way

Test it yourself with the code of section 9: build a tree from `range(500)` and from a shuffled copy, and print `height(...)` for both. Then insert the keys `4, 2, 6, 1, 3, 5, 7` and the keys `1` to `7` in sorted order, and print `to_level_list(...)` of both.

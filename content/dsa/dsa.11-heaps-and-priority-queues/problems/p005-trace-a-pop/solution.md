## Approach

Keep the list and the position `i` of the sinking item on paper. Each round: look at the children of `i` that exist, pick the smaller one if it is smaller than the sinking item, swap, move `i`. The loop prints `stop` when no child is smaller or when there are no children left.

## Expected output

```text
pop 1: move 8 to the root
[8, 2, 6, 3, 4, 7]
swap 8 with 2
[2, 8, 6, 3, 4, 7]
swap 8 with 3
[2, 3, 6, 8, 4, 7]
stop
1
pop 2: move 7 to the root
[7, 3, 6, 8, 4]
swap 7 with 3
[3, 7, 6, 8, 4]
swap 7 with 4
[3, 4, 6, 8, 7]
stop
2
[3, 4, 6, 8, 7]
```

## Why

| step | list before the loop step | `i` | children (index: value) | smaller child | action |
|---|---|---|---|---|---|
| pop 1, round 1 | `[8, 2, 6, 3, 4, 7]` | 0 | 1: 2, 2: 6 | 2 (index 1) | swap 8 and 2 |
| pop 1, round 2 | `[2, 8, 6, 3, 4, 7]` | 1 | 3: 3, 4: 4 | 3 (index 3) | swap 8 and 3 |
| pop 1, round 3 | `[2, 3, 6, 8, 4, 7]` | 3 | 7, 8 do not exist (`n = 6`) | none | `stop` |
| pop 2, round 1 | `[7, 3, 6, 8, 4]` | 0 | 1: 3, 2: 6 | 3 (index 1) | swap 7 and 3 |
| pop 2, round 2 | `[3, 7, 6, 8, 4]` | 1 | 3: 8, 4: 4 | 4 (index 4) | swap 7 and 4 |
| pop 2, round 3 | `[3, 4, 6, 8, 7]` | 4 | 9, 10 do not exist (`n = 5`) | none | `stop` |

Both pops needed two swaps: the heap has height 2, so two is also the most any pop on 6 or 7 items can need. In the second pop the moved item `7` met `8` and `4`: it must swap with the **smaller** one. If it swapped with `8`, the `4` would stay below a bigger parent and the heap rule would break. The result `[3, 4, 6, 8, 7]` is a valid heap and it is not sorted: `8` comes before `7`, but they are siblings (children of `4`), and the rule never compares siblings.

## Another way

Check yourself with the three invariants after each line: (1) the list is shorter by one than at the start of the pop; (2) only the sinking item moves **down**, and each swapped partner moves **up** by one level; (3) the first line printed after `pop ...` shows the list **before** any swap, with the moved item at index 0.

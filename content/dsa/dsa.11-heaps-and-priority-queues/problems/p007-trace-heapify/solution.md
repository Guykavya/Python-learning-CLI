## Approach

Walk the loop `i = 2, 1, 0` and keep the current list on paper. Print the `sift_down from index` line with the value at that index **at that moment**, then follow the sinking item: at each level compare the two children, take the smaller one if it is smaller than the sinking item, print a `swap` line (before the swap) and move on. After the call print the list.

## Expected output

```text
sift_down from index 2 (value 7)
swap a[2]=7 with a[5]=2
-> [9, 4, 2, 1, 6, 7, 8]
sift_down from index 1 (value 4)
swap a[1]=4 with a[3]=1
-> [9, 1, 2, 4, 6, 7, 8]
sift_down from index 0 (value 9)
swap a[0]=9 with a[1]=1
swap a[1]=9 with a[3]=4
-> [1, 4, 2, 9, 6, 7, 8]
total swaps: 4
[1, 4, 2, 9, 6, 7, 8]
```

## Why

| call | list before | item that sinks | children (index: value) | action |
|---|---|---|---|---|
| index 2 | `[9, 4, 7, 1, 6, 2, 8]` | 7 | 5: 2, 6: 8 | 2 is smaller: swap 7 and 2; 7 is at index 5, a leaf |
| index 1 | `[9, 4, 2, 1, 6, 7, 8]` | 4 | 3: 1, 4: 6 | 1 is smaller: swap 4 and 1; 4 is at index 3, a leaf |
| index 0 | `[9, 1, 2, 4, 6, 7, 8]` | 9 | 1: 1, 2: 2 | 1 is smaller: swap 9 and 1 |
| index 0, level 2 | `[1, 9, 2, 4, 6, 7, 8]` | 9 (now at index 1) | 3: 4, 4: 6 | 4 is smaller: swap 9 and 4; 9 is at index 3, a leaf |

Indexes 3, 4, 5 and 6 are leaves: a leaf is a heap of one item and needs no `sift_down`, so the loop starts at the last parent, `7 // 2 - 1 = 2`. When index 0 is handled, both of its subtrees are valid heaps (that is why the loop goes **backwards**), and one `sift_down` repairs the whole tree. Had the loop gone forwards, the 9 would have sunk into subtrees that were not heaps yet.

Pushing the seven numbers one by one gives the same list here, `[1, 4, 2, 9, 6, 7, 8]`, which is a coincidence of this input. For `7, 6, 5, 4, 3, 2, 1` the two methods differ: `heapify` gives `[1, 3, 2, 4, 6, 7, 5]` and the pushes give `[1, 4, 2, 7, 5, 6, 3]`. Both are valid heaps: a set of numbers has many valid heap arrangements, only the root is forced.

## Another way

Count the work instead of the lines: 4 swaps for 7 items. In general the total number of swaps of `heapify` is less than `n`, because a node at height `h` can sink at most `h` levels and most nodes have a small height. Pushing in the worst order (descending numbers) costs about `n log n` swaps.

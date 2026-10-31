## Hint 1

Draw the heap as a tree, level by level: index 0 on top, 1 and 2 below it, 3 4 5 6 below those. After each push, put the new item in the next free spot (the end of the list) and swap it upward only while it is smaller than its parent. Where does `1` end up when it is pushed into `[3, 5, 8]`?

## Hint 2

For `heappop`, the **last** item (not the second smallest!) jumps to the top and then sinks, always swapping with the **smaller** of its two children. `heappushpop(h, 0)` with `h[0] = 3`: is 0 `<=` the root? Then the heap does not change at all. `heapreplace` does not make that check.

## Hint 3

```
pushes:   [5] [3,5] [3,5,8] [1,3,8,5] [1,3,8,5,9] [1,3,2,5,9,8]
pop:      return 1, 8 goes to top and sinks past 2
pushpop 4: 4 > root 2, so return 2; 4 goes to top and sinks past 3
heapify [7,6,5,4,3,2,1]: sift index 2 (5), then index 1 (6), then index 0 (7)
max-heap: store -x, so the smallest stored value is minus the biggest x
```

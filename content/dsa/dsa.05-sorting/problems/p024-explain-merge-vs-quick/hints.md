## Hint 1

Which of the two has a trivial split (`mid = len // 2`) and a hard combine? Which has a hard split (partition) and a trivial combine (nothing)?

## Hint 2

Merge sort: always O(n log n), O(n) extra. Quick sort: O(n^2) worst case, O(log n) extra with a good recursion order, usually the fastest in practice for arrays in memory.

## Hint 3

Stability: the partition swaps elements across long distances, so equal elements can change order. Merge sort takes the left one first on ties.

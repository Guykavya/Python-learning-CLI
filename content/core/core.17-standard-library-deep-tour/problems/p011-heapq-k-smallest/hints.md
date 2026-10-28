## Hint 1

`heapq.nsmallest(k, nums)` returns a sorted list of the k smallest. `heapq.nlargest(k, records, key=...)` needs a key that picks the field out of a dict. What does `nsmallest` return for `k = 0` or a negative `k`?

## Hint 2

`heapify(lst)` rearranges `lst` **in place** in O(n). That is why you copy first: `heap = list(nums)`. After `heapify`, `heappop(heap)` removes and returns the smallest item each time. Stop when you have k items or the heap is empty.

## Hint 3

```
k_smallest(nums, k):   return heapq.nsmallest(k, nums) if k > 0 else []
top_k_by(recs, k, f):  return heapq.nlargest(k, recs, key=lambda r: r[f]) if k > 0 else []
pop_k_smallest(nums, k):
    heap = list(nums); heapify(heap)
    out = []
    while heap and len(out) < k: out.append(heappop(heap))
    return out
```

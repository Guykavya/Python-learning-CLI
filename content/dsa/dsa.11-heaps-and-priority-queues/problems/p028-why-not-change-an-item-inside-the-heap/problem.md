# Explain: why not change an item inside the heap?

A `heapq` heap is a plain list. So it is tempting to change the priority of an item with an assignment: "the job in slot 3 is more urgent now". Chapter section 5 warns against it, section 11 shows the replacement. Run this program (it is short and safe), then answer in `answer.md`.

```python
import heapq

def drain(heap):
    heap = list(heap)                       # work on a copy
    out = []
    while heap:
        out.append(heapq.heappop(heap))
    return out

heap = [1, 3, 2, 8, 5, 4, 7]
print(drain(heap))
heap[3] = 0                                 # "give the item 8 a better priority", in place
print(heap)
print(drain(heap))
```

Write an explanation (8 to 12 sentences) in `answer.md` that answers:

1. Why is the first printed line sorted? Which rule of a min-heap makes `heappop` return the items in order?
2. After `heap[3] = 0`, which pair of positions breaks the rule? Draw the tree of the list `[1, 3, 2, 0, 5, 4, 7]` and name the parent and the child.
3. The last line is **not** sorted. Which value comes out too late, and why does `heappop` not notice that it is the smallest number in the heap? (Think about which items `heappop` looks at.)
4. Name two correct ways to change a priority and say what each one costs in time and in memory: one that never changes an entry inside the heap, and one that changes it but repairs the heap. Which function of `heapq` repairs a heap completely, and what does it cost?
5. A friend stores entries as lists `[priority, count, task]` and marks an entry as removed by replacing the **task** field with a marker, in place. Why is that safe, while replacing the **priority** field in place is not?
6. What must a heap know about its items if you want to change the priority of an item in `O(log n)` without leaving stale entries behind?

Compare with the model answer and rate yourself.

## Hint 1

Try `[1, 8, 3, 5]` by hand with two different orders of joining and add the costs. Whose length is paid more often: a stick that is joined first or last? So which sticks should be joined first?

## Hint 2

Always join the **two shortest** sticks. The new stick may now be longer than others, so it must go back to where it belongs. You need "give me the smallest, remove it, put a new item in" many times: a min-heap does each in `O(log n)`.

## Hint 3

```
heap = copy of sticks, heapify
cost = 0
while the heap has at least 2 items:
    a = pop(heap)
    b = pop(heap)
    cost += a + b
    push(heap, a + b)
return cost
```

Heapify a **copy** (`list(sticks)`): `heapify` changes the list it gets.

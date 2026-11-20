## Hint 1

The smallest number overall is one of the **first** numbers of the lists. After you take it, which other number could be the next smallest? Only the number that comes right after it in the same list. So how many numbers must the heap hold at any time?

## Hint 2

A heap entry must tell you **where it came from**, so that you can push the next number of the same list: store `(value, list_number, position)`. The `list_number` also protects you when two values are equal: tuples are compared field by field, and `(5, 0, 2)` against `(5, 1, 0)` is decided by the second field, never by something that cannot be compared.

## Hint 3

```
heap = [(lst[0], i, 0) for each list i that is not empty]
heapify(heap)
result = []
while heap:
    value, i, j = pop(heap)
    result.append(value)
    if j + 1 < len(lists[i]):
        push(heap, (lists[i][j + 1], i, j + 1))
return result
```

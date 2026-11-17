# Trace a pop

This is the textbook `pop` of the chapter (section 3): remove the root, move the **last** item to the root, then let it sink by swapping with the **smaller** child. It prints what it does. Predict **exactly** what the program prints. Do not run it.

```python
def left(i):
    return 2 * i + 1

def right(i):
    return 2 * i + 2

def pop_traced(a):
    top = a[0]
    last = a.pop()
    print(f"pop {top}: move {last} to the root")
    if a:
        a[0] = last
        print(a)
        i, n = 0, len(a)
        while True:
            smallest = i
            if left(i) < n and a[left(i)] < a[smallest]:
                smallest = left(i)
            if right(i) < n and a[right(i)] < a[smallest]:
                smallest = right(i)
            if smallest == i:
                print("stop")
                break
            print(f"swap {a[i]} with {a[smallest]}")
            a[i], a[smallest] = a[smallest], a[i]
            i = smallest
            print(a)
    return top

heap = [1, 2, 6, 3, 4, 7, 8]
print(pop_traced(heap))
print(pop_traced(heap))
print(heap)
```

Write your answer in `answer.txt`, one printed line per line, in the order the program prints them. A list is printed the way Python prints it, for example `[8, 2, 6, 3, 4, 7]`. The function `print`s lines inside `pop_traced`, and the call `print(pop_traced(heap))` prints the returned value **after** those lines.

## How to work

Draw the tree of `[1, 2, 6, 3, 4, 7, 8]` first (index 0 is the root; the children of index `i` are `2i + 1` and `2i + 2`). Then do the first pop on paper:

1. `a.pop()` removes the **last** item (not the root). Write down the list before you put it into `a[0]`.
2. In the `while` loop, find the smaller of the (existing) children. Notice that `smallest` starts as `i`, so a child counts only if it is smaller than the best so far.
3. After every swap the sinking item has a new index: its children are now other nodes. The list printed has only `n = len(a)` items, one fewer than before.

Do the second pop on the list that the first one left behind.

## After you answer

1. How many swaps did each pop need, and what is the largest number of swaps a pop on a 6-item heap can need?
2. In the second pop, the moved item `7` met the children `8` and `4` at the second level. Why did it swap with `4` and not with `8`?
3. The final printed list is a valid heap, but it is not sorted. Which two items are "out of order", and why does the heap property not care?

## Hint 1

Window `3 -1 -3`, and the next element is 5. Can 3, -1 or -3 ever again be the maximum of a window that contains the 5?
(They leave the window before the 5 does, and they are smaller.) So which elements are worth remembering?

## Hint 2

Keep a deque of **indices** whose values decrease from front to back. A new index `i` first removes from the back
every index with a value `<= a[i]`, then joins at the back. The front is the maximum, unless it has left the window:
remove it when `dq[0] <= i - k`. Store indices, not values, so you can tell when an element is too old.

## Hint 3

```
dq = empty deque; out = []
for i in 0..n-1:
    while dq and a[dq[-1]] <= a[i]: dq.pop()
    dq.append(i)
    if dq[0] <= i - k: dq.popleft()
    if i >= k - 1: out.append(a[dq[0]])
print out separated by spaces
```

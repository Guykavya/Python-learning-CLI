## Hint 1

In a max-heap stored in a list, where is the largest value? After you move it to the end, what is damaged and how do you repair it?

## Hint 2

Only the root is wrong after the swap. `sift_down(0, end)` pushes it down, choosing the **larger** child each time, until it is not smaller than both children. The heap region shrinks to `a[0:end]`.

## Hint 3

```
def sift_down(a, i, size):
    while True:
        l, r, big = 2*i+1, 2*i+2, i
        if l < size and a[l] > a[big]: big = l
        if r < size and a[r] > a[big]: big = r
        if big == i: return
        a[i], a[big] = a[big], a[i]; i = big
```

## Hint 1

Why is an already sorted list the worst case for 'last element as pivot'? What would a better pivot be?

## Hint 2

Pick `pivot = a[random.randrange(len(a))]`. Make three lists with comprehensions: `less`, `equal`, `greater`. Return `quick(less) + equal + quick(greater)`. The equal part is never recursed into, so all-equal input costs O(n).

## Hint 3

```
def quick(a):
    if len(a) <= 1: return a
    pivot = a[random.randrange(len(a))]
    less = [x for x in a if x < pivot]; equal = [x for x in a if x == pivot]; greater = [x for x in a if x > pivot]
    return quick(less) + equal + quick(greater)
```

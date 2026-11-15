## Approach

The minimum of a stack only depends on the items below the top and the top itself, and the items below never change while the top is there. So at push time we can record "the minimum from the bottom up to here" next to the new item. After any number of pops, the new top carries the minimum of exactly the items that remain.

## Code

```python
class MinStack:
    def __init__(self):
        self.items = []                      # (value, minimum up to here)

    def push(self, x):
        current_min = min(x, self.items[-1][1]) if self.items else x
        self.items.append((x, current_min))

    def pop(self):
        return self.items.pop()[0]

    def top(self):
        return self.items[-1][0]

    def get_min(self):
        return self.items[-1][1]
```

## Complexity

Every operation is `O(1)`. Memory is `O(n)`, with one extra number per item.

## Another way

Two stacks: the items, and a second stack `mins` that receives `x` only when `x <= mins[-1]` (a new minimum or a tie). On `pop`, if the popped value equals `mins[-1]`, pop `mins` too. This saves memory when new minimums are rare. The `<=` is essential: problem 21 is about what happens with `<`.

## Approach

`pop` removes the top of `mins` whenever the popped value **equals** the current minimum. `push` only recorded values that were **strictly** smaller. With two equal minimums, `mins` held one copy, and the first `pop` removed it although another copy was still in `items`. The two methods must agree: if `pop` removes on equality, `push` must record on equality.

## Code

```python
class MinStack:
    def __init__(self):
        self.items = []
        self.mins = []

    def push(self, x):
        self.items.append(x)
        if not self.mins or x <= self.mins[-1]:     # was: x < self.mins[-1]
            self.mins.append(x)

    def pop(self):
        x = self.items.pop()
        if x == self.mins[-1]:
            self.mins.pop()
        return x

    def top(self):
        return self.items[-1]

    def get_min(self):
        return self.mins[-1]
```

## Complexity

All operations stay `O(1)`. `mins` holds one entry per value that was a minimum (or tied with it) when it arrived; for increasing input it stays at one entry.

## Another way

Store `[value, count]` in `mins`: an equal value increases the count instead of adding an entry, and `pop` decreases it, removing the entry at 0. This uses even less memory when the same minimum is pushed many times. The pair-per-item design of problem 20 avoids the subtle case entirely, at the cost of one extra number per item.

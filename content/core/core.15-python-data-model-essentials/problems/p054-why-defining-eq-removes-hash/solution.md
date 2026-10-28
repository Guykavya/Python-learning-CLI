## Approach

Answer in the order of the four questions: observe, state the contract, give the repairs, warn about
mutation. Compare with `answer.md`.

## Code

```python
class A:
    def __init__(self, n):
        self.n = n

    def __eq__(self, other):
        return isinstance(other, A) and self.n == other.n

    def __hash__(self):
        return hash(self.n)


print(len({A(1), A(1)}))      # 1
```

## Complexity

Hashing makes set and dict lookups O(1) on average. A constant hash (`return 1`) would keep the
contract but make every lookup O(n).

## Another way

`@dataclass(frozen=True)` generates both `__eq__` and `__hash__` from the same fields, which removes
the chance of making them disagree.

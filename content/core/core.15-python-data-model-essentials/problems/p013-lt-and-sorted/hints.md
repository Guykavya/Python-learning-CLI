## Hint 1

Which operator does `sorted` use between two items? If you only define `<`, how can `a > b` still work? (Hint: Python tries `b < a`.)

## Hint 2

Compare `(self.priority, self.name)` with `(other.priority, other.name)`: tuples compare item by item, which gives "priority first, name on ties" for free. Do not forget the type check.

## Hint 3

```
def __lt__(self, other):
    if not isinstance(other, Task): return NotImplemented
    return (self.priority, self.name) < (other.priority, other.name)
```

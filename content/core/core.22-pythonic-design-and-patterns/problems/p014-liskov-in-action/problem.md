# Trace: Liskov in action

The **Liskov substitution principle** says: code written for a parent class must keep working
when you hand it any subclass. A subclass breaks it when it demands more than the parent
(refuses inputs the parent accepted), or promises less (does something other than the parent
promised).

Below, `Stack` has a clear contract (see the docstring), and `reverse_all` and `check` are written
only against `Stack`. Five subclasses follow. Some keep the contract, some break it.

Work out, **line by line**, what the program prints. The last five lines print the class name,
whether it is a subclass of `Stack`, and whether it uses the very same `push` function as `Stack`
(`is` tests identity). The program is deterministic and needs no input.

```python
class Stack:
    """Contract: after push(x), len grows by 1 and pop() returns x (last in, first out)."""

    def __init__(self):
        self.items = []

    def push(self, x):
        self.items.append(x)

    def pop(self):
        return self.items.pop()

    def __len__(self):
        return len(self.items)


class LimitedStack(Stack):
    def __init__(self, limit):
        super().__init__()
        self.limit = limit

    def push(self, x):
        if len(self.items) >= self.limit:
            raise OverflowError("full")
        super().push(x)


class DedupStack(Stack):
    def push(self, x):
        if x not in self.items:
            super().push(x)


class CountingStack(Stack):
    def __init__(self):
        super().__init__()
        self.pushes = 0

    def push(self, x):
        self.pushes += 1
        super().push(x)


class FrozenStack(Stack):
    def push(self, x):
        raise TypeError("read-only")


def reverse_all(stack, items):
    for x in items:
        stack.push(x)
    out = []
    while len(stack) > 0:
        out.append(stack.pop())
    return out


def check(label, stack, items):
    try:
        result = reverse_all(stack, items)
    except Exception as e:
        print(label, "raised", type(e).__name__)
        return
    expected = list(reversed(items))
    print(label, "ok" if result == expected else "wrong", result)


check("plain", Stack(), [1, 2, 3])
check("limit3", LimitedStack(3), [1, 2, 3])
check("limit2", LimitedStack(2), [1, 2, 3])
check("dedup", DedupStack(), [1, 2, 3])
check("dedup-repeat", DedupStack(), [1, 2, 1])
counting = CountingStack()
check("counting", counting, [4, 5])
print("pushes", counting.pushes)
check("frozen", FrozenStack(), [1])
check("frozen-empty", FrozenStack(), [])
for cls in (Stack, LimitedStack, DedupStack, CountingStack, FrozenStack):
    print(cls.__name__, issubclass(cls, Stack), cls.push is Stack.push)
```

Write your answer in `answer.txt`, one output line per `print`.

After you have the output, look at it again and ask: **which subclasses are safe substitutes
for `Stack`, and which break the contract?** (`solution.md` has the discussion; the checked answer
is only the printed output.)

**Example (a different program)**

```python
class A:
    def f(self): return 1
class B(A):
    def f(self): return 2
print(A().f(), B().f(), B.f is A.f)
```

prints

```
1 2 False
```

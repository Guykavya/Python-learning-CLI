## Approach

Each op has a fixed number of values it needs. Checking that number *before* touching the stack
gives a clear `StackUnderflow` with the offset, instead of a random `IndexError` halfway through
an instruction. One private helper runs the program and tracks both the stack and the deepest
size seen, so `simulate` and `max_depth` cannot disagree.

## Code

```python
class StackUnderflow(Exception):
    """An instruction needed more values than the stack had."""


NEEDS = {"PUSH": 0, "POP": 1, "DUP": 1, "SWAP": 2, "ADD": 2, "MUL": 2}


def _run(ops):
    stack = []
    deepest = 0
    for offset, (op, arg) in enumerate(ops):
        if op not in NEEDS:
            raise ValueError(f"unknown op {op!r} at offset {offset}")
        need = NEEDS[op]
        if len(stack) < need:
            raise StackUnderflow(f"{op} at offset {offset} needs {need} values, stack has {len(stack)}")
        if op == "PUSH":
            stack.append(arg)
        elif op == "POP":
            stack.pop()
        elif op == "DUP":
            stack.append(stack[-1])
        elif op == "SWAP":
            stack[-1], stack[-2] = stack[-2], stack[-1]
        else:
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b if op == "ADD" else a * b)
        deepest = max(deepest, len(stack))
    return stack, deepest


def simulate(ops):
    return _run(ops)[0]


def max_depth(ops):
    return _run(ops)[1]
```

## Complexity

O(n) time for n instructions; O(d) extra space where d is the maximum depth.

## Another way

Dispatch through a dict of small functions instead of an `if` chain, which is closer to how a
real interpreter's dispatch table works:

```python
def _add(stack, arg):
    b, a = stack.pop(), stack.pop()
    stack.append(a + b)

HANDLERS = {"ADD": (2, _add), "PUSH": (0, lambda s, arg: s.append(arg)), ...}
```

`max_depth` can also be computed *without running anything*, from stack effects alone (PUSH +1,
POP -1, DUP +1, SWAP 0, ADD -1, MUL -1). That is what CPython's compiler does for
`co_stacksize`: it never knows your values, only how many there will be.

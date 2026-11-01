class StackUnderflow(Exception):
    """An instruction needed more values than the stack had."""


NEEDS = {"PUSH": 0, "POP": 1, "DUP": 1, "SWAP": 2, "ADD": 2, "MUL": 2}


def _run(ops):
    """Run ops; return (final stack, deepest stack size seen)."""
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
    """Run (op, arg) instructions on an empty stack; return the final stack (bottom first)."""
    return _run(ops)[0]


def max_depth(ops):
    """Largest stack size reached while running ops."""
    return _run(ops)[1]

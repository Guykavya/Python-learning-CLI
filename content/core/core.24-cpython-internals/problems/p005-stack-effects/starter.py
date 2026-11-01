class StackUnderflow(Exception):
    """An instruction needed more values than the stack had."""


def simulate(ops):
    """Run (op, arg) instructions on an empty stack; return the final stack (bottom first)."""
    stack = []
    # TODO: one branch per op; check the stack is deep enough before popping
    return stack


def max_depth(ops):
    """Largest stack size reached while running ops."""
    # TODO
    return 0

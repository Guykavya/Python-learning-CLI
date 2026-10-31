## Approach

Start from the rewrite rule `total = log_calls(total)`. Everything else follows from it: it runs once at
definition time, and afterwards the name refers to the wrapper, whose own name and docstring are those of
`def wrapper`. `wraps` repairs the labels by copying them from the original.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Show it in the shell: `print(total)` gives `<function log_calls.<locals>.wrapper at 0x...>` (the address is
machine-specific). After adding `@wraps(func)` it gives `<function total at 0x...>`, and
`total.__wrapped__` is the original undecorated function.

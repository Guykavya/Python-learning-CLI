# Trace: a stack after each operation

Predict **exactly** what this program prints. Do not run it.

```python
stack = []
for op in ["push 4", "push 7", "pop", "push 1", "push 9", "pop", "pop", "push 5"]:
    if op == "pop":
        x = stack.pop()
        print("pop", x, stack)
    else:
        stack.append(int(op.split()[1]))
        print(op, stack)
print("top", stack[-1], "size", len(stack))
```

Write your answer in `answer.txt`, one printed line per line, exactly as Python prints it, for example `push 4 [4]` (the operation, then the list with a comma and a space between items).

## How to work

Draw the list horizontally with the **top on the right**. `append` adds on the right; `pop()` removes from the right and returns that item. Update your drawing after every operation before you write its line.

## After you answer

1. Which value has been on the stack the longest by the end?
2. If every `pop` were `pop(0)`, what would the last line print?
3. How many items were ever pushed, and how many are left? How many pops does that mean?

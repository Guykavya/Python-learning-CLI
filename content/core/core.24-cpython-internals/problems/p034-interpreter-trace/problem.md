# Trace: run the mini VM by hand

Below is a tiny virtual machine for the instruction set of the module project (p035), and a
short program for it. After **every** instruction the VM prints one line: the offset of the
instruction it just ran, its op, how many frames exist, and the stack of the **current** frame
(after the instruction). `PRINT` also prints a line `out <value>` just before its own trace line.

Work out the whole output by hand, the way CPython's evaluation loop would run it, without
running the code. Keep a little table: `pc`, the frames, and each frame's stack.

Facts you may need:

- `pc` is moved to the next instruction **before** the instruction runs, so a jump simply
  overwrites it, and `CALL` stores the already-advanced `pc` as the return address.
- `JUMP_IF_FALSE` always pops its condition, and jumps only when that value is `0`.
- `CALL (target, nargs)` moves the top `nargs` values (in the same order) from the caller's stack
  into a **new** frame's stack. `RET` pops the return value, removes the frame and pushes the
  value on the caller's stack.
- For `SUB`, the top of the stack is the right operand: `[a, b]` becomes `[a - b]`.

```python
def run(program, max_steps=100):
    frames = [{"stack": [], "vars": {}, "ret": None}]
    pc = steps = 0
    while pc < len(program):
        steps += 1
        if steps > max_steps:
            raise RuntimeError("step limit")
        offset = pc
        op, arg = program[offset]
        pc = offset + 1
        stack = frames[-1]["stack"]
        if op == "PUSH":
            stack.append(arg)
        elif op == "DUP":
            stack.append(stack[-1])
        elif op == "SWAP":
            stack[-1], stack[-2] = stack[-2], stack[-1]
        elif op in ("ADD", "SUB", "MUL"):
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b if op == "ADD" else a - b if op == "SUB" else a * b)
        elif op == "JUMP":
            pc = arg
        elif op == "JUMP_IF_FALSE":
            if stack.pop() == 0:
                pc = arg
        elif op == "PRINT":
            print("out", stack.pop())
        elif op == "CALL":
            target, nargs = arg
            args = stack[len(stack) - nargs:]
            del stack[len(stack) - nargs:]
            frames.append({"stack": args, "vars": {}, "ret": pc})
            pc = target
        elif op == "RET":
            value = stack.pop()
            pc = frames.pop()["ret"]
            frames[-1]["stack"].append(value)
        elif op == "HALT":
            pc = len(program)
        print(offset, op, f"depth={len(frames)}", f"stack={frames[-1]['stack']}")


program = [
    ("PUSH", 2),            # 0
    ("DUP", None),          # 1   loop:
    ("JUMP_IF_FALSE", 10),  # 2   -> end
    ("DUP", None),          # 3
    ("PUSH", 10),           # 4
    ("CALL", (11, 2)),      # 5   -> f with 2 arguments
    ("PRINT", None),        # 6
    ("PUSH", 1),            # 7
    ("SUB", None),          # 8
    ("JUMP", 1),            # 9   -> loop
    ("HALT", None),         # 10  end:
    ("SWAP", None),         # 11  f:
    ("SUB", None),          # 12
    ("RET", None),          # 13
]

run(program)
```

**Example**: the first two lines are

```
0 PUSH depth=1 stack=[2]
1 DUP depth=1 stack=[2, 2]
```

Write in `answer.txt` all the lines the program prints, in order (30 lines).

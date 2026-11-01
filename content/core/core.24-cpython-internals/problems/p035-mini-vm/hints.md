## Hint 1

Build in layers and run one test group at a time.

1. **Assembler** (`pytest -k TestAssembler`). Why can a jump not be resolved while you read the
   text line by line? (Think of `JUMP end` where `end:` comes later.) What does a label count:
   lines, or instructions? What must you remember about every instruction so that a later error
   can still name its line?
2. **Step limit and `step()`** (`-k TestStepLimit`, `-k TestStepMethod`). Build this before the
   jumps. Where in `step()` must the check go so that a program needing exactly `max_steps`
   steps still finishes? Which offset does the failing instruction have if you advance `pc`
   before executing it?
3. **Stack, arithmetic, variables, jumps.** For `SUB`, which value comes off the stack first, and
   is it `a` or `b` in `a - b`? Does `JUMP_IF_FALSE` pop when it does *not* jump?
4. **CALL/RET.** What must a frame contain so that a recursive call cannot overwrite the
   caller's `n`? Where is the return address stored?
5. **Compiler.** A `BinOp` node has `left`, `op`, `right`. In which order must you emit them so
   that the right operand ends up on top? For a `while`, you need to jump to an offset you do not
   know yet: how can you fill it in later?

## Hint 2

```
assemble(text):
    labels = {}; rows = []
    for number, raw in enumerate(lines, start=1):
        line = raw before '#', stripped;  skip if empty
        if line ends with ':': check name, not a duplicate; labels[name] = len(rows); continue
        op, *operands = line.split()
        check op is known and len(operands) is right (CALL: 2, no-arg ops: 0, others: 1)
        rows.append((number, op, operands))
    second pass: build (op, arg): int(...) for PUSH and nargs, labels[name] for targets,
                 each error raises AssemblyError(message, number)

step():
    if halted or pc >= len(program): return False
    offset = pc
    if steps >= max_steps: raise StepLimitExceeded(..., offset)
    steps += 1; op, arg = program[offset]; pc = offset + 1
    dispatch on op        # every error uses offset, never pc
    return True

binary op:   b = pop(); a = pop(); push(a OP b)
JUMP_IF_FALSE: if pop() == 0: pc = target
CALL (target, n): check len(stack) >= n; args = last n values (removed);
                  frame = Frame(return_pc=offset + 1); frame.stack = args; frames.append(frame); pc = target
RET:   if only main frame: VMError; value = pop(); frame = frames.pop(); push(value) on the new top frame
       pc = frame.return_pc

compile while:
    start = len(code); compile test
    j = emit("JUMP_IF_FALSE", None)         # remember its index
    compile body; emit("JUMP", start)
    code[j] = ("JUMP_IF_FALSE", len(code))  # patch: the end is known now
compile a > b:  a, b, SWAP, LT
compile -x:     PUSH 0, x, SUB
```

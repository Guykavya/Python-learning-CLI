# Project: a mini stack-based bytecode VM

CPython runs your code in three stages: the compiler turns source into bytecode, and the
evaluation loop in `ceval.c` runs that bytecode one instruction at a time on a value stack, with
one **frame** per function call. In this project you build the same machine in miniature:

1. an **assembler** that turns readable text into a list of instructions,
2. a **virtual machine** (VM) with a value stack, variables, jumps, function calls with frames,
   clear errors and a step limit,
3. a small **compiler** that uses `ast` to turn a tiny subset of Python into instructions for your VM.

After this you can read a `dis` listing and *see* the machine moving. This is the module project;
take your time and build it layer by layer.

Copy `starter.py` to `solution.py`. The error classes and the `Frame` class are already written.

## The instruction set

A program is a list of `(op, arg)` tuples. `arg` is `None` for ops that take no operand.
"Top" is the last value pushed; "second" is the value below it.

| Op | Arg in the program | Effect |
|---|---|---|
| `PUSH n` | int `n` | push `n` |
| `POP` | `None` | pop and discard the top |
| `DUP` | `None` | push another copy of the top |
| `SWAP` | `None` | exchange top and second |
| `ADD` `SUB` `MUL` | `None` | pop top `b`, pop second `a`, push `a + b` / `a - b` / `a * b` |
| `DIV` | `None` | same, pushes `a // b` (floor division, like Python); `b == 0` raises `VMError` |
| `LT` `EQ` | `None` | same, pushes the int `1` if `a < b` / `a == b`, else `0` |
| `LOAD name` | str | push the value of the variable `name` in the current frame; `UndefinedName` if it has none |
| `STORE name` | str | pop the top and store it in the variable `name` of the current frame |
| `JUMP label` | int target | continue at the target offset |
| `JUMP_IF_FALSE label` | int target | **pop** the top; if it is `0`, continue at the target (it pops in both cases) |
| `PRINT` | `None` | pop the top and append it to `vm.output` |
| `CALL label nargs` | tuple `(target, nargs)` | call a function (see below) |
| `RET` | `None` | return from a function (see below) |
| `HALT` | `None` | stop the program |

The program also ends normally when `pc` moves past the last instruction. A jump target may be
anything from `0` to `len(program)` (the end); any other target raises `VMError`.

**Frames.** Each function call gets a fresh `Frame` with its **own** stack and its **own**
variables (it cannot see the caller's). `CALL (target, nargs)` removes the top `nargs` values
from the caller's stack (fewer than `nargs`: `StackUnderflow`) and puts them on the new frame's
stack **in the same order**, so the last argument is on top. The frame remembers the return
address (the offset after the `CALL`), and execution jumps to `target`. `RET` pops the return
value from the callee's stack, throws the frame away, pushes the value on the caller's stack and
continues at the return address. `RET` in the main frame raises `VMError`.

## Part 1: `assemble(text)`

Assembler text has one instruction per line: the op name in upper case, then its operands,
separated by spaces. A line `name:` defines a label: the offset of the **next** instruction.
Everything after `#` is a comment; blank lines and indentation are ignored.

```
    PUSH 5
    CALL fact 1        # CALL label nargs
    PRINT
    HALT
fact:
    STORE n
    ...
```

`assemble` returns the list of tuples with labels replaced by offsets: `PUSH` gets an `int`,
`LOAD`/`STORE` a `str`, jumps an `int`, `CALL` a tuple `(target, nargs)`. A label may be used
before it is defined. Any problem raises `AssemblyError(message, line)` where `line` is the
1-based line number in the text: an unknown op, a wrong number of operands, a non-integer where
an integer is needed, an undefined label, or a label defined twice.

## Part 2: `VM(program, max_steps=10_000)`

The starter gives you the attributes: `program`, `max_steps`, `frames` (a list, main frame
first), `output`, `pc`, `steps` and `halted`, and the properties `stack` and `variables` (of the
current frame). Write:

- `step()`: run **one** instruction and return `True`. If the program has already finished
  (halted, or `pc` past the end), return `False` and count nothing. Before running an
  instruction, if `steps` has already reached `max_steps`, raise `StepLimitExceeded`. So a
  program that needs exactly `max_steps` steps still finishes. `HALT` counts as a step.
- `run()`: call `step()` until it returns `False`, then return `output`.
- `run_source(text, max_steps=10_000)`: assemble, run, return the output.

**Errors.** Every runtime error is a `VMError` (or a subclass) whose `offset` is the index of the
instruction that failed (not `pc + 1`): `StackUnderflow` when an op needs more values than the
current frame's stack has, `UnknownOp` for an op the VM does not know, `UndefinedName`,
`StepLimitExceeded`, and plain `VMError` for division by zero, a bad jump target and `RET`
outside a function.

## Part 3: `compile_source(source)`

Compile this subset of Python with `ast.parse` into a program for your VM (a list of tuples):

- statements: `name = expr`, `print(expr)` (exactly one argument), `while test:` (no `else`),
  `if test:` with optional `elif`/`else`;
- expressions: int literals, names, `+ - * //`, unary `-`, and one comparison `<`, `>` or `==`.

Anything else (strings, `**`, `/`, `True`, chained comparisons, `def`, tuple assignment,
`print` with two arguments) raises `CompileError`. The VM has no `GT`: compile `a > b` as `b < a`.
All variables live in the main frame.

## Example

```python
>>> program = assemble("PUSH 10\nPUSH 3\nSUB\nPRINT")
>>> program
[('PUSH', 10), ('PUSH', 3), ('SUB', None), ('PRINT', None)]
>>> VM(program).run()
[7]
>>> run_source("PUSH 1\nSTORE n\nloop:\nJUMP loop", max_steps=100)
Traceback (most recent call last):
  ...
StepLimitExceeded: offset 2: more than 100 steps
>>> compile_source("x = 2\nprint(x * 21)")
[('PUSH', 2), ('STORE', 'x'), ('LOAD', 'x'), ('PUSH', 21), ('MUL', None), ('PRINT', None)]
```

(The exact error message text is up to you; the tests check the class and `offset`.)

The tests are grouped by feature: `TestAssembler`, `TestStackOps`, `TestArithmetic`,
`TestVariables`, `TestJumps`, `TestCallRet`, `TestErrors`, `TestStepLimit`, `TestStepMethod`,
`TestCompiler`. Work through them in that order with `pytest -k TestAssembler` and so on, but
build the step limit early: it turns an endless loop into a clear error.

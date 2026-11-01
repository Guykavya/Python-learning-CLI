## Approach

The machine has three layers, and each one mirrors a part of CPython:

1. **The assembler is a two-pass translator.** Pass one reads the lines, records every label as
   "the offset of the next instruction" and keeps each instruction with its line number. Pass
   two turns operands into values and labels into offsets. Two passes are needed because a jump
   may name a label defined later (every `if` and `while` jumps forward). CPython's compiler does
   the same when it assigns final offsets to jump targets.
2. **The VM is a fetch-decode-execute loop.** `step()` saves `offset = pc`, checks the step limit,
   fetches `program[offset]`, moves `pc` to the next instruction and then executes, possibly
   changing `pc` again (jumps, calls, returns). That is exactly what CPython's evaluation loop
   does with `next_instr`. Every error uses the saved `offset`, so messages point at the
   instruction that failed. **Frames** make calls work: each call gets its own stack and
   variables, and a list of frames is the call stack. Recursion is just more frames in the list,
   so it is limited by the step limit, never by Python's own recursion limit.
3. **The compiler walks the `ast`** and emits postfix code: operands first, operator last. That is
   why `dis` shows `LOAD x`, `LOAD y`, `BINARY_OP +`. Forward jumps are emitted with a
   placeholder target and **patched** once the end of the block is known.

## Code

```python
"""Mini stack-based bytecode VM: an assembler, an interpreter with frames, and a tiny compiler."""

import ast

# --------------------------------------------------------------------------- errors


class AssemblyError(Exception):
    """Bad assembler text. `line` is the 1-based line number in the text."""

    def __init__(self, message, line):
        super().__init__(f"line {line}: {message}")
        self.line = line


class VMError(Exception):
    """A runtime error. `offset` is the index of the instruction that failed."""

    def __init__(self, message, offset):
        super().__init__(f"offset {offset}: {message}")
        self.offset = offset


class StackUnderflow(VMError):
    pass


class UnknownOp(VMError):
    pass


class UndefinedName(VMError):
    pass


class StepLimitExceeded(VMError):
    pass


class CompileError(Exception):
    pass


# --------------------------------------------------------------------------- instruction set

NO_ARG = {"POP", "DUP", "SWAP", "ADD", "SUB", "MUL", "DIV", "LT", "EQ", "PRINT", "RET", "HALT"}
INT_ARG = {"PUSH"}
NAME_ARG = {"LOAD", "STORE"}
LABEL_ARG = {"JUMP", "JUMP_IF_FALSE"}
CALL_ARG = {"CALL"}
OPS = NO_ARG | INT_ARG | NAME_ARG | LABEL_ARG | CALL_ARG

BINARY = {
    "ADD": lambda a, b: a + b,
    "SUB": lambda a, b: a - b,
    "MUL": lambda a, b: a * b,
    "LT": lambda a, b: 1 if a < b else 0,
    "EQ": lambda a, b: 1 if a == b else 0,
}


# --------------------------------------------------------------------------- assembler


def _parse_int(token, line):
    try:
        return int(token)
    except ValueError:
        raise AssemblyError(f"{token!r} is not an integer", line) from None


def assemble(text):
    """Turn assembler text into a list of (op, arg) tuples with label names resolved to offsets."""
    labels = {}
    rows = []  # (line number, op, operands) of real instructions
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.endswith(":"):
            name = line[:-1].strip()
            if not name.isidentifier():
                raise AssemblyError(f"bad label name {name!r}", number)
            if name in labels:
                raise AssemblyError(f"label {name!r} defined twice", number)
            labels[name] = len(rows)  # the offset of the NEXT instruction
            continue
        op, *operands = line.split()
        if op not in OPS:
            raise AssemblyError(f"unknown op {op!r}", number)
        expected = 0 if op in NO_ARG else 2 if op in CALL_ARG else 1
        if len(operands) != expected:
            raise AssemblyError(f"{op} takes {expected} operand(s), got {len(operands)}", number)
        rows.append((number, op, operands))

    def target(name, number):
        if name not in labels:
            raise AssemblyError(f"undefined label {name!r}", number)
        return labels[name]

    program = []
    for number, op, operands in rows:
        if op in NO_ARG:
            arg = None
        elif op in INT_ARG:
            arg = _parse_int(operands[0], number)
        elif op in NAME_ARG:
            if not operands[0].isidentifier():
                raise AssemblyError(f"bad variable name {operands[0]!r}", number)
            arg = operands[0]
        elif op in LABEL_ARG:
            arg = target(operands[0], number)
        else:  # CALL label nargs
            nargs = _parse_int(operands[1], number)
            if nargs < 0:
                raise AssemblyError("nargs cannot be negative", number)
            arg = (target(operands[0], number), nargs)
        program.append((op, arg))
    return program


# --------------------------------------------------------------------------- virtual machine


class Frame:
    """One function activation: its own operand stack, variables and return address."""

    def __init__(self, return_pc=None):
        self.stack = []
        self.variables = {}
        self.return_pc = return_pc


class VM:
    def __init__(self, program, max_steps=10_000):
        self.program = list(program)
        self.max_steps = max_steps
        self.frames = [Frame()]
        self.output = []
        self.pc = 0
        self.steps = 0
        self.halted = False

    @property
    def stack(self):
        return self.frames[-1].stack

    @property
    def variables(self):
        return self.frames[-1].variables

    def _pop(self, offset):
        if not self.stack:
            raise StackUnderflow("pop from an empty stack", offset)
        return self.stack.pop()

    def _jump(self, target, offset):
        if not isinstance(target, int) or not 0 <= target <= len(self.program):
            raise VMError(f"bad jump target {target!r}", offset)
        self.pc = target

    def step(self):
        """Run one instruction. Return False (and count nothing) if the program has finished."""
        if self.halted or self.pc >= len(self.program):
            return False
        offset = self.pc
        if self.steps >= self.max_steps:
            raise StepLimitExceeded(f"more than {self.max_steps} steps", offset)
        self.steps += 1
        op, arg = self.program[offset]
        self.pc = offset + 1

        if op == "PUSH":
            self.stack.append(arg)
        elif op == "POP":
            self._pop(offset)
        elif op == "DUP":
            value = self._pop(offset)
            self.stack.extend([value, value])
        elif op == "SWAP":
            b = self._pop(offset)
            a = self._pop(offset)
            self.stack.extend([b, a])
        elif op in BINARY or op == "DIV":
            b = self._pop(offset)  # the top is the RIGHT operand
            a = self._pop(offset)
            if op == "DIV":
                if b == 0:
                    raise VMError("division by zero", offset)
                self.stack.append(a // b)
            else:
                self.stack.append(BINARY[op](a, b))
        elif op == "LOAD":
            if arg not in self.variables:
                raise UndefinedName(f"name {arg!r} is not defined", offset)
            self.stack.append(self.variables[arg])
        elif op == "STORE":
            self.variables[arg] = self._pop(offset)
        elif op == "JUMP":
            self._jump(arg, offset)
        elif op == "JUMP_IF_FALSE":
            if self._pop(offset) == 0:
                self._jump(arg, offset)
        elif op == "PRINT":
            self.output.append(self._pop(offset))
        elif op == "CALL":
            target, nargs = arg
            if len(self.stack) < nargs:
                raise StackUnderflow(f"CALL needs {nargs} argument(s)", offset)
            args = self.stack[len(self.stack) - nargs:]
            del self.stack[len(self.stack) - nargs:]
            frame = Frame(return_pc=offset + 1)
            frame.stack.extend(args)
            self.frames.append(frame)
            self._jump(target, offset)
        elif op == "RET":
            if len(self.frames) == 1:
                raise VMError("RET outside a function", offset)
            value = self._pop(offset)
            frame = self.frames.pop()
            self.stack.append(value)
            self.pc = frame.return_pc
        elif op == "HALT":
            self.halted = True
        else:
            raise UnknownOp(f"unknown op {op!r}", offset)
        return True

    def run(self):
        while self.step():
            pass
        return self.output


def run_source(text, max_steps=10_000):
    """Assemble and run; return the printed values."""
    return VM(assemble(text), max_steps).run()


# --------------------------------------------------------------------------- compiler

BIN_OPS = {ast.Add: "ADD", ast.Sub: "SUB", ast.Mult: "MUL", ast.FloorDiv: "DIV"}


class Compiler:
    def __init__(self):
        self.code = []

    def emit(self, op, arg=None):
        self.code.append((op, arg))
        return len(self.code) - 1  # its offset, so a jump can be patched later

    def patch(self, offset, target):
        op, _ = self.code[offset]
        self.code[offset] = (op, target)

    # ----- statements
    def statement(self, node):
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                raise CompileError("only 'name = expression' assignments are supported")
            self.expression(node.value)
            self.emit("STORE", node.targets[0].id)
        elif isinstance(node, ast.Expr) and self.is_print(node.value):
            self.expression(node.value.args[0])
            self.emit("PRINT")
        elif isinstance(node, ast.While) and not node.orelse:
            start = len(self.code)
            self.expression(node.test)
            exit_jump = self.emit("JUMP_IF_FALSE")
            self.block(node.body)
            self.emit("JUMP", start)
            self.patch(exit_jump, len(self.code))
        elif isinstance(node, ast.If):
            self.expression(node.test)
            else_jump = self.emit("JUMP_IF_FALSE")
            self.block(node.body)
            if node.orelse:
                end_jump = self.emit("JUMP")
                self.patch(else_jump, len(self.code))
                self.block(node.orelse)
                self.patch(end_jump, len(self.code))
            else:
                self.patch(else_jump, len(self.code))
        else:
            raise CompileError(f"unsupported statement: {type(node).__name__}")

    def block(self, statements):
        for node in statements:
            self.statement(node)

    @staticmethod
    def is_print(node):
        return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "print" and len(node.args) == 1 and not node.keywords)

    # ----- expressions
    def expression(self, node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            self.emit("PUSH", node.value)
        elif isinstance(node, ast.Name):
            self.emit("LOAD", node.id)
        elif isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            self.expression(node.left)
            self.expression(node.right)
            self.emit(BIN_OPS[type(node.op)])
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            self.emit("PUSH", 0)
            self.expression(node.operand)
            self.emit("SUB")
        elif isinstance(node, ast.Compare) and len(node.ops) == 1:
            op, right = node.ops[0], node.comparators[0]
            self.expression(node.left)
            self.expression(right)
            if isinstance(op, ast.Lt):
                self.emit("LT")
            elif isinstance(op, ast.Gt):  # a > b  is  b < a
                self.emit("SWAP")
                self.emit("LT")
            elif isinstance(op, ast.Eq):
                self.emit("EQ")
            else:
                raise CompileError(f"unsupported comparison: {type(op).__name__}")
        else:
            raise CompileError(f"unsupported expression: {type(node).__name__}")


def compile_source(source):
    """Compile a tiny Python subset into a VM program."""
    compiler = Compiler()
    compiler.block(ast.parse(source).body)
    return compiler.code
```

Notes on the trickier parts:

- **`step()` order.** Finished check, then the step limit, then `steps += 1`, then execute. A
  `step()` call that finds the program finished counts nothing, and the limit fires *before* the
  instruction that would be one too many, so `vm.steps == max_steps` after the error.
- **`JUMP_IF_FALSE` always pops.** The condition is consumed whether or not the jump is taken; that
  is why a compiled loop leaves the stack empty.
- **`CALL` copies arguments in order** (`self.stack[len - nargs:]`), so the callee's first `STORE`
  takes the last argument. `RET` pops the frame *before* pushing, so the value lands on the caller's
  stack.
- **Comparisons push ints.** `1 if a < b else 0`, not `a < b`.
- **`a > b` with no `GT` op**: compile `a`, `b`, then `SWAP` turns the stack into `b, a` and `LT`
  computes `b < a`. CPython's compiler also has to choose instructions for every source construct;
  `elif` for example is just an `If` inside `orelse`, so the same code handles it.

## Complexity

Assembling is O(L) for L lines (two passes, dict lookups for labels). Each VM step is O(1),
except `CALL` which copies `nargs` values, so a run costs O(steps), at most O(max_steps). The
compiler visits each `ast` node once: O(nodes). Memory: the program, plus one frame per active
call (bounded by the step limit).

## Another way

Keep **one shared value stack** and give each frame only a *base pointer* (the index where its
part of the stack begins): `CALL` records `base = len(data) - nargs`, an underflow is
`len(data) <= base`, and `RET` deletes `data[base:]` before pushing the result. This is closer
to CPython, where a frame's value stack is a slice at the end of one big per-thread data stack.
Dispatch can also use methods named after the ops:

```python
handler = getattr(self, "op_" + op, None)
if handler is None:
    raise UnknownOp(f"unknown op {op!r}", offset)
handler(arg, offset)
```

For the compiler you can emit **assembler text** with generated labels (`L1:`, `JUMP L1`) and
call your own `assemble()` at the end; the two-pass assembler then does the patching for you.

Ideas to extend the project (not tested): a disassembler for your bytecode (problem p031),
`AND`/`OR` with short-circuit jumps, `def` statements compiled to `CALL`/`RET`, a constant pool
like `co_consts`, or a peephole pass that folds `PUSH 2, PUSH 3, ADD` into `PUSH 5`.

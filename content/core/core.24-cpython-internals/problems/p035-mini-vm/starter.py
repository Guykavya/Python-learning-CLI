"""Mini stack-based bytecode VM: an assembler, an interpreter with frames, and a tiny compiler."""

import ast


# --------------------------------------------------------------------------- errors (done for you)


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


# --------------------------------------------------------------------------- part 1: assembler


def assemble(text):
    """Turn assembler text into a list of (op, arg) tuples with labels resolved to offsets."""
    # TODO: pass 1 collects labels and instruction rows, pass 2 builds the tuples
    raise NotImplementedError


# --------------------------------------------------------------------------- part 2: the VM


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

    def step(self):
        """Run one instruction and return True, or return False if the program has finished."""
        # TODO: check the step limit FIRST, then fetch, advance pc, execute
        raise NotImplementedError

    def run(self):
        """Run until the program finishes; return self.output."""
        raise NotImplementedError


def run_source(text, max_steps=10_000):
    """Assemble and run; return the printed values."""
    raise NotImplementedError


# --------------------------------------------------------------------------- part 3: the compiler


def compile_source(source):
    """Compile a tiny Python subset (see problem.md) into a VM program."""
    tree = ast.parse(source)
    # TODO: walk tree.body and emit (op, arg) tuples; patch jump targets afterwards
    raise NotImplementedError

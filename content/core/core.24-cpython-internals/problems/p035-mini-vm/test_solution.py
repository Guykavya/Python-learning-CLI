"""Mini VM tests, grouped by feature. Run one group with: pytest -k TestAssembler

Every test that runs a program passes a small max_steps, so a bug that makes a loop
infinite ends with StepLimitExceeded instead of freezing your computer (once your step
limit works; build it early).
"""

import threading

import pytest

from solution import (
    VM,
    AssemblyError,
    CompileError,
    StackUnderflow,
    StepLimitExceeded,
    UndefinedName,
    UnknownOp,
    VMError,
    assemble,
    compile_source,
    run_source,
)

LIMIT = 2_000
ALL_OPS = {"PUSH", "POP", "DUP", "SWAP", "ADD", "SUB", "MUL", "DIV", "LT", "EQ", "LOAD", "STORE",
           "JUMP", "JUMP_IF_FALSE", "PRINT", "CALL", "RET", "HALT"}


def run(text, max_steps=LIMIT):
    return run_source(text, max_steps=max_steps)


def vm_after(text, max_steps=LIMIT):
    vm = VM(assemble(text), max_steps=max_steps)
    vm.run()
    return vm


def run_guarded(vm, seconds=10):
    """Run vm.run() in a helper thread so a VM that ignores max_steps cannot hang the tests."""
    box = {}

    def target():
        try:
            box["output"] = vm.run()
        except BaseException as error:  # noqa: BLE001 - we hand every error back to the test
            box["error"] = error

    worker = threading.Thread(target=target, daemon=True)
    worker.start()
    worker.join(seconds)
    if worker.is_alive():
        pytest.fail("The VM was still running after 10 s. Count every executed instruction in self.steps "
                    "and raise StepLimitExceeded before running one more than max_steps.")
    return box


# =========================================================================== assembler
class TestAssembler:
    def test_simple_program(self):
        assert assemble("PUSH 2\nPUSH 3\nADD\nPRINT\n") == [
            ("PUSH", 2), ("PUSH", 3), ("ADD", None), ("PRINT", None)
        ], "Each line becomes one (op, arg) tuple; ops without an operand get arg None; PUSH's operand is an int."

    def test_blank_lines_comments_and_indentation(self):
        text = """
            # a full-line comment

            PUSH 7      # trailing comment
                PRINT
        """
        assert assemble(text) == [("PUSH", 7), ("PRINT", None)], (
            "Strip everything after '#', strip spaces, and skip empty lines."
        )

    def test_negative_numbers(self):
        assert assemble("PUSH -12") == [("PUSH", -12)], "int('-12') handles the sign; keep PUSH's operand an int."

    def test_names(self):
        assert assemble("PUSH 1\nSTORE total\nLOAD total") == [
            ("PUSH", 1), ("STORE", "total"), ("LOAD", "total")
        ], "LOAD and STORE keep their operand as a string (the variable name)."

    def test_labels_become_offsets(self):
        text = """
        start:
            PUSH 1
            JUMP_IF_FALSE end
            JUMP start
        end:
            HALT
        """
        assert assemble(text) == [("PUSH", 1), ("JUMP_IF_FALSE", 3), ("JUMP", 0), ("HALT", None)], (
            "A label names the offset of the NEXT instruction. Label lines are not instructions themselves."
        )

    def test_forward_reference(self):
        prog = assemble("JUMP skip\nPUSH 1\nPRINT\nskip:\nPUSH 2\nPRINT")
        assert prog[0] == ("JUMP", 3), (
            "A jump may name a label defined further down. Collect all labels first (first pass), then resolve."
        )

    def test_label_at_the_very_end(self):
        prog = assemble("PUSH 0\nJUMP_IF_FALSE done\nPUSH 1\ndone:")
        assert prog[1] == ("JUMP_IF_FALSE", 3), (
            "A label after the last instruction points at len(program): jumping there ends the program."
        )

    def test_call_operand(self):
        prog = assemble("PUSH 4\nCALL square 1\nHALT\nsquare:\nDUP\nMUL\nRET")
        assert prog[1] == ("CALL", (3, 1)), "CALL label nargs becomes ('CALL', (target_offset, nargs))."

    @pytest.mark.parametrize("text, line, why", [
        ("PUSH 1\nFLY 3\n", 2, "an unknown op"),
        ("PUSH\n", 1, "PUSH without its operand"),
        ("PUSH 1\nADD 5\n", 2, "an operand on an op that takes none"),
        ("PUSH x\n", 1, "PUSH with a non-integer operand"),
        ("PUSH 1\n\nJUMP nowhere\n", 3, "a jump to an undefined label"),
        ("a:\nPUSH 1\na:\nHALT\n", 3, "a label defined twice"),
        ("PUSH 1\nCALL f\nf:\nRET\n", 2, "CALL without nargs"),
        ("PUSH 1\nCALL f two\nf:\nRET\n", 2, "CALL with a non-integer nargs"),
    ])
    def test_errors_name_the_line(self, text, line, why):
        with pytest.raises(AssemblyError) as info:
            assemble(text)
        assert info.value.line == line, (
            f"For {why}, raise AssemblyError with .line = {line} (1-based, counting blank and comment lines too)."
        )


# =========================================================================== stack ops
class TestStackOps:
    def test_push_pop(self):
        vm = vm_after("PUSH 1\nPUSH 2\nPUSH 3\nPOP")
        assert vm.stack == [1, 2], "POP removes the top (last) value. vm.stack is the current frame's stack."

    def test_dup(self):
        assert vm_after("PUSH 5\nDUP").stack == [5, 5], "DUP pushes a second copy of the top value."

    def test_swap(self):
        assert vm_after("PUSH 1\nPUSH 2\nSWAP").stack == [2, 1], "SWAP exchanges the two top values."

    def test_print_pops(self):
        vm = vm_after("PUSH 4\nPUSH 9\nPRINT")
        assert vm.output == [9], "PRINT appends the top value to vm.output."
        assert vm.stack == [4], "PRINT also pops the value it prints."

    def test_run_returns_output(self):
        assert VM(assemble("PUSH 1\nPRINT\nPUSH 2\nPRINT"), max_steps=LIMIT).run() == [1, 2], (
            "run() returns the list of printed values, in order."
        )

    def test_empty_program(self):
        assert VM([], max_steps=LIMIT).run() == [], "An empty program finishes at once with no output."


# =========================================================================== arithmetic
class TestArithmetic:
    def test_add_mul(self):
        assert run("PUSH 2\nPUSH 3\nADD\nPUSH 4\nMUL\nPRINT") == [20], "(2 + 3) * 4 = 20."

    def test_sub_operand_order(self):
        assert run("PUSH 10\nPUSH 3\nSUB\nPRINT") == [7], (
            "SUB computes (second from top) - (top): 10 - 3 = 7. The top of the stack is the RIGHT operand."
        )

    def test_div_is_floor_division(self):
        assert run("PUSH 17\nPUSH 5\nDIV\nPRINT") == [3], "DIV is integer division a // b: 17 // 5 = 3."
        assert run("PUSH -7\nPUSH 2\nDIV\nPRINT") == [-4], "DIV floors like Python's //: -7 // 2 = -4."
        assert run("PUSH 2\nPUSH 8\nDIV\nPRINT") == [0], "2 // 8 = 0: the top (8) is the divisor."

    def test_div_by_zero(self):
        with pytest.raises(VMError) as info:
            run("PUSH 1\nPUSH 0\nDIV")
        assert info.value.offset == 2, "Division by zero raises VMError with the offset of the DIV (2)."

    def test_comparisons_push_one_or_zero(self):
        assert run("PUSH 2\nPUSH 5\nLT\nPRINT\nPUSH 5\nPUSH 2\nLT\nPRINT") == [1, 0], (
            "LT pushes 1 if (second) < (top), else 0: 2 < 5 -> 1, 5 < 2 -> 0."
        )
        assert run("PUSH 3\nPUSH 3\nEQ\nPRINT\nPUSH 3\nPUSH 4\nEQ\nPRINT") == [1, 0], "EQ pushes 1 or 0."

    def test_comparison_results_are_ints(self):
        out = run("PUSH 1\nPUSH 2\nLT\nPRINT")
        assert type(out[0]) is int, "LT and EQ push the int 1 or 0, not True/False: the VM only knows integers."


# =========================================================================== variables
class TestVariables:
    def test_store_and_load(self):
        vm = vm_after("PUSH 42\nSTORE x\nLOAD x\nLOAD x\nADD\nPRINT")
        assert vm.output == [84], "LOAD pushes the variable's value; it can be loaded many times."
        assert vm.variables == {"x": 42}, "vm.variables holds the current frame's variables."

    def test_store_pops(self):
        assert vm_after("PUSH 1\nPUSH 2\nSTORE y").stack == [1], "STORE pops the value it stores."

    def test_store_overwrites(self):
        assert run("PUSH 1\nSTORE x\nPUSH 2\nSTORE x\nLOAD x\nPRINT") == [2], "A second STORE replaces the value."

    def test_undefined_name(self):
        with pytest.raises(UndefinedName) as info:
            run("PUSH 1\nSTORE a\nLOAD b")
        assert info.value.offset == 2, "LOAD of a name never stored raises UndefinedName at the LOAD's offset (2)."


# =========================================================================== jumps
class TestJumps:
    def test_jump_skips(self):
        assert run("JUMP over\nPUSH 1\nPRINT\nover:\nPUSH 2\nPRINT") == [2], "JUMP sets pc to its target."

    def test_jump_if_false_pops_when_jumping(self):
        vm = vm_after("PUSH 9\nPUSH 0\nJUMP_IF_FALSE end\nPUSH 1\nend:")
        assert vm.stack == [9], "JUMP_IF_FALSE pops the condition: 0 is false, so it jumps, and the 0 is gone."

    def test_jump_if_false_pops_when_not_jumping(self):
        vm = vm_after("PUSH 9\nPUSH 1\nJUMP_IF_FALSE end\nPUSH 7\nend:")
        assert vm.stack == [9, 7], (
            "JUMP_IF_FALSE pops the condition even when it does NOT jump (nonzero is true)."
        )

    def test_countdown_loop(self):
        text = """
            PUSH 3
            STORE n
        loop:
            LOAD n
            JUMP_IF_FALSE done
            LOAD n
            PRINT
            LOAD n
            PUSH 1
            SUB
            STORE n
            JUMP loop
        done:
            HALT
        """
        assert run(text) == [3, 2, 1], "A loop: test n, jump to done when it is 0, else print and decrement."

    def test_sum_loop_leaves_clean_stack(self):
        text = """
            PUSH 0
            STORE total
            PUSH 1
            STORE i
        loop:
            LOAD i
            PUSH 11
            LT
            JUMP_IF_FALSE done
            LOAD total
            LOAD i
            ADD
            STORE total
            LOAD i
            PUSH 1
            ADD
            STORE i
            JUMP loop
        done:
            LOAD total
            PRINT
        """
        vm = vm_after(text)
        assert vm.output == [55], "1 + 2 + ... + 10 = 55."
        assert vm.stack == [], "If values pile up on the stack, JUMP_IF_FALSE is not popping its condition."

    def test_halt_stops(self):
        vm = vm_after("PUSH 1\nPRINT\nHALT\nPUSH 2\nPRINT")
        assert vm.output == [1], "Nothing after HALT runs."

    def test_bad_jump_target(self):
        with pytest.raises(VMError) as info:
            VM([("PUSH", 1), ("JUMP", 99)], max_steps=LIMIT).run()
        assert info.value.offset == 1, "A jump outside 0..len(program) raises VMError at the jump's offset."


# =========================================================================== CALL / RET
SQUARE = """
    PUSH 100
    PUSH 7
    CALL square 1
    ADD
    PRINT
    HALT
square:
    STORE n
    LOAD n
    LOAD n
    MUL
    RET
"""

SUBTRACT = """
    PUSH 10
    PUSH 3
    CALL minus 2
    PRINT
    HALT
minus:          # minus(a, b) = a - b
    STORE b     # the last argument is on top
    STORE a
    LOAD a
    LOAD b
    SUB
    RET
"""

FACTORIAL = """
    PUSH 5
    CALL fact 1
    PRINT
    HALT
fact:
    STORE n
    LOAD n
    PUSH 2
    LT
    JUMP_IF_FALSE recurse
    PUSH 1
    RET
recurse:
    LOAD n
    LOAD n
    PUSH 1
    SUB
    CALL fact 1
    MUL
    RET
"""


class TestCallRet:
    def test_call_returns_a_value(self):
        assert run(SQUARE) == [149], (
            "square(7) = 49 is pushed on the CALLER's stack, under which 100 is still waiting: 100 + 49 = 149."
        )

    def test_argument_order(self):
        assert run(SUBTRACT) == [7], (
            "CALL moves the nargs top values to the new frame in the same order, so the LAST argument is on top."
        )

    def test_callee_has_its_own_variables(self):
        text = """
            PUSH 1
            STORE n
            PUSH 5
            CALL f 1
            PRINT
            LOAD n
            PRINT
            HALT
        f:
            STORE n
            LOAD n
            RET
        """
        assert run(text) == [5, 1], "Each frame has its own variables: the function's n must not overwrite main's n."

    def test_callee_cannot_see_caller_variables(self):
        text = "PUSH 1\nSTORE secret\nCALL f 0\nHALT\nf:\nLOAD secret\nRET"
        with pytest.raises(UndefinedName) as info:
            run(text)
        assert info.value.offset == 4, "A new frame starts with NO variables; LOAD secret inside f must fail."

    def test_callee_has_its_own_stack(self):
        text = "PUSH 1\nPUSH 2\nCALL f 0\nHALT\nf:\nPOP"
        with pytest.raises(StackUnderflow) as info:
            run(text)
        assert info.value.offset == 4, (
            "The callee's stack starts with only its nargs arguments; it cannot pop the caller's values."
        )

    def test_recursion(self):
        assert run(FACTORIAL) == [120], "fact(5) = 120. Every CALL needs a fresh frame, or n gets overwritten."

    def test_frames_restored_after_return(self):
        vm = vm_after(FACTORIAL)
        assert len(vm.frames) == 1, "After every RET only the main frame is left in vm.frames."
        assert vm.stack == [], "The main stack is empty after PRINT."

    def test_nested_calls(self):
        text = """
            PUSH 3
            CALL quad 1
            PRINT
            HALT
        double:
            DUP
            ADD
            RET
        quad:
            CALL double 1
            CALL double 1
            RET
        """
        assert run(text) == [12], "A function can call another; each RET goes back to its own caller."

    def test_ret_outside_function(self):
        with pytest.raises(VMError) as info:
            run("PUSH 1\nRET")
        assert info.value.offset == 1, "RET in the main frame (no caller) raises VMError."

    def test_call_with_too_few_arguments(self):
        with pytest.raises(StackUnderflow) as info:
            run("PUSH 1\nCALL f 2\nf:\nRET")
        assert info.value.offset == 1, "CALL f 2 with one value on the stack raises StackUnderflow at the CALL."

    def test_ret_with_empty_stack(self):
        with pytest.raises(StackUnderflow) as info:
            run("CALL f 0\nHALT\nf:\nRET")
        assert info.value.offset == 2, "RET pops the return value; an empty callee stack is a StackUnderflow."


# =========================================================================== errors
class TestErrors:
    @pytest.mark.parametrize("text, offset, why", [
        ("POP", 0, "POP on an empty stack"),
        ("PUSH 1\nADD", 1, "ADD with only one value"),
        ("PUSH 1\nPRINT\nPRINT", 2, "PRINT on an empty stack"),
        ("DUP", 0, "DUP on an empty stack"),
        ("PUSH 1\nSWAP", 1, "SWAP with one value"),
        ("STORE x", 0, "STORE with nothing to store"),
        ("JUMP_IF_FALSE end\nend:", 0, "JUMP_IF_FALSE with no condition"),
    ])
    def test_stack_underflow(self, text, offset, why):
        with pytest.raises(StackUnderflow) as info:
            run(text)
        assert info.value.offset == offset, (
            f"{why}: StackUnderflow with .offset = {offset}, the index of the failing instruction (not pc + 1)."
        )

    def test_unknown_op(self):
        with pytest.raises(UnknownOp) as info:
            VM([("PUSH", 1), ("PUSH", 2), ("FLY", None)], max_steps=LIMIT).run()
        assert info.value.offset == 2, "An op the VM does not know raises UnknownOp with its offset."

    def test_error_hierarchy(self):
        for cls in (StackUnderflow, UnknownOp, UndefinedName, StepLimitExceeded):
            assert issubclass(cls, VMError), f"{cls.__name__} must subclass VMError, so one except catches them all."
        assert not issubclass(AssemblyError, VMError), "AssemblyError is about text, not running: keep it separate."

    def test_message_mentions_offset(self):
        with pytest.raises(StackUnderflow) as info:
            run("PUSH 1\nPUSH 2\nPOP\nPOP\nPOP")
        assert "4" in str(info.value), "The error message should say where it happened (offset 4)."


# =========================================================================== step limit
class TestStepLimit:
    def test_steps_are_counted(self):
        vm = vm_after("PUSH 1\nPRINT\nHALT\nPUSH 2")
        assert vm.steps == 3, "vm.steps counts executed instructions; HALT counts, the skipped PUSH does not."

    def test_exact_limit_is_allowed(self):
        assert run("PUSH 1\nPRINT\nHALT", max_steps=3) == [1], (
            "A program that needs exactly max_steps steps must finish: raise only before step max_steps + 1."
        )

    def test_one_step_too_many(self):
        with pytest.raises(StepLimitExceeded) as info:
            run("PUSH 1\nPRINT\nHALT", max_steps=2)
        assert info.value.offset == 2, "The error carries the offset of the instruction that could not run (HALT, 2)."

    def test_infinite_loop_stops(self):
        vm = VM(assemble("top:\nPUSH 1\nPOP\nJUMP top"), max_steps=1_000)
        box = run_guarded(vm)
        assert isinstance(box.get("error"), StepLimitExceeded), "An endless loop must end with StepLimitExceeded."
        assert vm.steps == 1_000, "Exactly max_steps instructions run before the error."

    def test_infinite_recursion_stops(self):
        vm = VM(assemble("CALL f 0\nf:\nCALL f 0"), max_steps=500)
        box = run_guarded(vm)
        assert isinstance(box.get("error"), StepLimitExceeded), (
            "Endless CALLs must hit the step limit too (not RecursionError: your VM keeps frames in a list)."
        )

    def test_default_limit(self):
        assert VM([]).max_steps == 10_000, "max_steps defaults to 10_000."


# =========================================================================== step()
class TestStepMethod:
    def test_step_by_step(self):
        vm = VM(assemble("PUSH 2\nPUSH 3\nADD"), max_steps=LIMIT)
        assert vm.step() is True and vm.stack == [2] and vm.pc == 1, "step() runs ONE instruction and returns True."
        vm.step()
        vm.step()
        assert vm.stack == [5], "After three steps the ADD has run."
        assert vm.step() is False, "step() returns False once the program has finished."
        assert vm.steps == 3, "A step() call that finds the program finished does not count as a step."

    def test_step_after_halt(self):
        vm = VM(assemble("HALT\nPUSH 1"), max_steps=LIMIT)
        assert vm.step() is True, "HALT is a real instruction: step() runs it and returns True."
        assert vm.step() is False, "After HALT, step() returns False and runs nothing."
        assert vm.stack == [], "The PUSH after HALT must not run."


# =========================================================================== compiler
def compiled(source, max_steps=LIMIT):
    program = compile_source(source)
    assert isinstance(program, list), "compile_source returns a list of (op, arg) tuples."
    for op, _arg in program:
        assert op in ALL_OPS, f"compile_source produced {op!r}, which is not in the instruction set."
    vm = VM(program, max_steps=max_steps)
    return vm.run(), vm


class TestCompiler:
    def test_print_constant_expression(self):
        assert compiled("print(2 + 3 * 4)")[0] == [14], (
            "Compile a BinOp as: left, right, then the op. The ast already encodes precedence: 2 + (3 * 4)."
        )

    def test_operand_order(self):
        assert compiled("print(10 - 4)\nprint(9 // 2)")[0] == [6, 4], (
            "Compile the LEFT operand first, so the right one ends on top: 10 - 4, 9 // 2."
        )

    def test_assignments_and_names(self):
        out, vm = compiled("x = 6\ny = x * 7\nprint(y)")
        assert out == [42], "Assignment: compile the value, then STORE name. A Name compiles to LOAD."
        assert vm.variables == {"x": 6, "y": 42}, "Both variables end up in the main frame."

    def test_unary_minus(self):
        assert compiled("print(-5 + 2)\nx = 3\nprint(-x)")[0] == [-3, -3], (
            "-expr is a UnaryOp(USub) node: compile it as 0 - expr."
        )

    def test_comparisons(self):
        out = compiled("print(1 < 2)\nprint(2 < 1)\nprint(3 == 3)\nprint(5 > 2)\nprint(2 > 5)")[0]
        assert out == [1, 0, 1, 1, 0], (
            "< is LT, == is EQ, and a > b is b < a (compile a and b, then SWAP and LT)."
        )

    def test_while_loop(self):
        source = """
total = 0
i = 1
while i < 11:
    total = total + i
    i = i + 1
print(total)
"""
        assert compiled(source)[0] == [55], (
            "while: start: <test>; JUMP_IF_FALSE end; <body>; JUMP start; end:. Patch the end target afterwards."
        )

    def test_if_else(self):
        source = """
n = 1
while n < 7:
    if n // 2 * 2 == n:
        print(n)
    else:
        print(0 - n)
    n = n + 1
"""
        assert compiled(source)[0] == [-1, 2, -3, 4, -5, 6], (
            "if/else: <test>; JUMP_IF_FALSE else; <body>; JUMP end; else: <orelse>; end:."
        )

    def test_if_without_else_and_elif(self):
        source = """
x = 5
if x < 3:
    print(1)
elif x < 10:
    print(2)
else:
    print(3)
if x == 0:
    print(99)
print(x)
"""
        assert compiled(source)[0] == [2, 5], (
            "elif is an If inside orelse; an if without else jumps straight past its body."
        )

    def test_nested_loops(self):
        source = """
count = 0
i = 0
while i < 4:
    j = 0
    while j < 3:
        count = count + 1
        j = j + 1
    i = i + 1
print(count)
"""
        assert compiled(source)[0] == [12], "Nested loops need their own start and end targets: 4 * 3 = 12."

    def test_compiled_program_leaves_empty_stack(self):
        _, vm = compiled("i = 0\nwhile i < 3:\n    i = i + 1\nprint(i)")
        assert vm.stack == [], "Statements must leave the stack as they found it."

    @pytest.mark.parametrize("source", [
        "x = 2 ** 3",
        "x = 'hi'",
        "print(1, 2)",
        "a, b = 1, 2",
        "def f():\n    pass",
        "x = 1 < 2 < 3",
        "x = 7 / 2",
        "x = True",
    ])
    def test_unsupported_code(self, source):
        with pytest.raises(CompileError):
            compile_source(source)

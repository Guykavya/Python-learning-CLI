import pytest

import solution
from solution import COMMANDS, register, run_command


def test_register_stores_and_returns_func():
    table = {}

    def hello():
        return "hi"

    result = register(table, "hi")(hello)
    assert table == {"hi": hello}, "register(table, name)(func) must store func in table[name]."
    assert result is hello, "Return the function unchanged, so the name in the module still works."


def test_decorator_syntax():
    table = {}

    @register(table, "double")
    def double(x):
        return 2 * x

    assert double(4) == 8, "After @register the function must still be callable as normal. Did you forget `return func`?"
    assert table["double"] is double, "The registered function and the module name must be the same object."


def test_duplicate_name():
    table = {}
    register(table, "x")(lambda: 1)
    with pytest.raises(ValueError) as info:
        register(table, "x")(lambda: 2)
    assert str(info.value) == "command already registered: x", "Refuse a second function with the same name; do not silently overwrite."
    assert table["x"]() == 1, "The first registration must stay."


def test_commands_table():
    assert set(COMMANDS) == {"add", "neg", "total"}, "COMMANDS must hold exactly add, neg and total, registered with @register(COMMANDS, ...)."
    assert solution.add(10, 1) == 11, "add must still be a normal function in the module."


def test_run_command():
    assert run_command(COMMANDS, "add 2 3") == 5, "Split the line, turn the rest into ints, call registry[name](*numbers)."
    assert run_command(COMMANDS, "neg 7") == -7, "neg takes one number."
    assert run_command(COMMANDS, "total 1 2 3 4") == 10, "Pass the numbers as SEPARATE arguments with *numbers, not as one list."
    assert run_command(COMMANDS, "total") == 0, "No numbers: call total() with no arguments."
    assert run_command(COMMANDS, "  add   -4   9 ") == 5, "Use line.split() with no argument, so extra spaces do not matter."


def test_run_command_errors():
    with pytest.raises(ValueError) as info:
        run_command(COMMANDS, "mul 2 3")
    assert str(info.value) == "unknown command: mul", "An unknown name must raise ValueError('unknown command: <name>'), not KeyError."
    with pytest.raises(ValueError) as info:
        run_command(COMMANDS, "   ")
    assert str(info.value) == "empty command", "A blank line has no command name."


def test_run_command_other_table():
    table = {}
    register(table, "mul")(lambda a, b: a * b)
    assert run_command(table, "mul 6 7") == 42, "run_command must use the registry it is given, not always COMMANDS."

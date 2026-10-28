import pytest

from solution import Command, Delete, Editor, Insert, Macro, NothingToRedo, NothingToUndo


def test_command_is_abstract():
    with pytest.raises(TypeError):
        Command()

    class Half(Command):
        def do(self, editor):
            pass

    with pytest.raises(TypeError):
        Half()  # undo and describe are still abstract


def test_exceptions():
    assert str(NothingToUndo()) == "nothing to undo", "NothingToUndo() has the message 'nothing to undo'."
    assert str(NothingToRedo()) == "nothing to redo", "NothingToRedo() has the message 'nothing to redo'."


def test_insert_do_undo():
    ed = Editor("hello")
    ed.execute(Insert(5, " world"))
    assert ed.text == "hello world", "Insert at the end (pos == len(text)) is allowed."
    ed.execute(Insert(0, ">> "))
    assert ed.text == ">> hello world", "Insert at 0 puts the text in front."
    ed.undo()
    assert ed.text == "hello world", "undo removes exactly the inserted text."


def test_insert_in_the_middle():
    ed = Editor("abef")
    ed.execute(Insert(2, "cd"))
    assert ed.text == "abcdef", "text[:pos] + new + text[pos:]."


@pytest.mark.parametrize("pos", [-1, 6])
def test_insert_out_of_range(pos):
    ed = Editor("hello")
    with pytest.raises(IndexError, match=f"insert position {pos} out of range"):
        ed.execute(Insert(pos, "x"))
    assert ed.text == "hello" and not ed.can_undo(), "A failed command changes nothing and is not recorded."


def test_delete_do_undo():
    ed = Editor("hello world")
    ed.execute(Delete(5, 6))
    assert ed.text == "hello", "Delete(5, 6) removes ' world'."
    ed.undo()
    assert ed.text == "hello world", "undo puts the removed text back."


@pytest.mark.parametrize("pos, length", [(3, 3), (-1, 1), (5, 1)])
def test_delete_out_of_range(pos, length):
    ed = Editor("hello")
    with pytest.raises(IndexError, match=f"delete range {pos}..{pos + length} out of range"):
        ed.execute(Delete(pos, length))
    assert ed.text == "hello" and not ed.can_undo(), "A failed delete changes nothing and is not recorded."


def test_delete_everything():
    ed = Editor("abc")
    ed.execute(Delete(0, 3))
    assert ed.text == "", "Deleting the whole text is allowed."
    ed.undo()
    assert ed.text == "abc"


def test_describe():
    assert Insert(5, " world").describe() == "insert ' world' at 5", "Insert.describe uses repr of the text."
    assert Delete(0, 1).describe() == "delete 1 at 0", "Delete.describe format."
    assert Macro("greet", [Insert(0, "a"), Insert(0, "b")]).describe() == "macro greet (2 steps)", "Macro.describe format."


def test_history_and_example():
    ed = Editor("hello")
    ed.execute(Insert(5, " world"))
    ed.execute(Delete(0, 1))
    assert ed.text == "ello world"
    assert ed.history() == ["insert ' world' at 5", "delete 1 at 0"], "history() lists describe() of done commands, oldest first."
    ed.undo()
    assert ed.text == "hello world" and ed.history() == ["insert ' world' at 5"], "undo removes the command from the history."
    ed.redo()
    assert ed.text == "ello world", "redo does the command again."
    ed.undo()
    ed.undo()
    assert ed.text == "hello", "Undo everything: back to the start."
    with pytest.raises(NothingToUndo, match="nothing to undo"):
        ed.undo()


def test_history_is_a_copy():
    ed = Editor()
    ed.execute(Insert(0, "x"))
    ed.history().clear()
    assert ed.history() == ["insert 'x' at 0"], "history() returns a NEW list."


def test_redo_empty():
    ed = Editor("a")
    with pytest.raises(NothingToRedo, match="nothing to redo"):
        ed.redo()


def test_new_command_clears_redo():
    ed = Editor("abc")
    ed.execute(Insert(3, "d"))
    ed.undo()
    assert ed.can_redo(), "After undo there is something to redo."
    ed.execute(Insert(0, "z"))
    assert not ed.can_redo(), "A new command clears the redo stack."
    with pytest.raises(NothingToRedo):
        ed.redo()


def test_failed_command_keeps_redo():
    ed = Editor("abc")
    ed.execute(Insert(3, "d"))
    ed.undo()
    with pytest.raises(IndexError):
        ed.execute(Delete(10, 1))
    assert ed.can_redo(), "Only a SUCCESSFUL command clears the redo stack."


def test_can_undo_redo():
    ed = Editor()
    assert (ed.can_undo(), ed.can_redo()) == (False, False), "A new editor has nothing to undo or redo."
    ed.execute(Insert(0, "a"))
    assert (ed.can_undo(), ed.can_redo()) == (True, False)
    ed.undo()
    assert (ed.can_undo(), ed.can_redo()) == (False, True)


def test_many_undo_redo_rounds():
    ed = Editor("")
    for i, ch in enumerate("python"):
        ed.execute(Insert(i, ch))
    ed.execute(Delete(0, 2))
    assert ed.text == "thon"
    for _ in range(7):
        ed.undo()
    assert ed.text == "" and not ed.can_undo(), "Seven commands, seven undos."
    for _ in range(7):
        ed.redo()
    assert ed.text == "thon", "Redoing everything gives the same text again."


def test_macro_do_undo():
    ed = Editor("world")
    ed.execute(Macro("greet", [Insert(0, "hello "), Insert(11, "!"), Delete(0, 1)]))
    assert ed.text == "ello world!", "A macro runs its commands in order."
    assert ed.history() == ["macro greet (3 steps)"], "A macro is ONE entry in the history."
    ed.undo()
    assert ed.text == "world", "Undoing a macro undoes its commands in reverse order."
    ed.redo()
    assert ed.text == "ello world!", "Redo runs the macro again."


def test_macro_rolls_back_on_failure():
    ed = Editor("hello")
    with pytest.raises(IndexError, match="delete range 100..101 out of range"):
        ed.execute(Macro("bad", [Insert(0, "Oh, "), Insert(4, "my "), Delete(100, 1)]))
    assert ed.text == "hello", "When a step fails, undo the steps that already ran (in reverse), then re-raise."
    assert not ed.can_undo(), "A failed macro is not recorded."


def test_macro_inside_macro():
    inner = Macro("inner", [Insert(0, "b"), Insert(0, "a")])
    ed = Editor("c")
    ed.execute(Macro("outer", [inner, Insert(3, "d")]))
    assert ed.text == "abcd", "A Macro is a Command, so it can contain other macros."
    ed.undo()
    assert ed.text == "c", "Undoing nested macros restores the text."


def test_execute_needs_a_command():
    class Fake:
        def do(self, editor):
            editor.text = "hacked"

    ed = Editor("safe")
    with pytest.raises(TypeError, match=r"execute\(\) needs a Command"):
        ed.execute(Fake())
    assert ed.text == "safe", "Check the type before calling do()."

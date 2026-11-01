import pytest

from solution import Delete, Editor, History, Insert, Macro, Replace


class Fake:
    def __init__(self, name, log, fail=False):
        self.name, self.log, self.fail = name, log, fail

    def do(self):
        if self.fail:
            raise RuntimeError(f"{self.name} failed")
        self.log.append(f"do {self.name}")

    def undo(self):
        self.log.append(f"undo {self.name}")


def test_insert_exact():
    ed = Editor("ac")
    cmd = Insert(ed, 1, "b")
    cmd.do()
    assert ed.text == "abc", f"Insert(1, 'b') into 'ac' must give 'abc', got {ed.text!r}."
    cmd.undo()
    assert ed.text == "ac", f"Insert.undo must remove exactly what was inserted, got {ed.text!r}."


def test_insert_at_both_ends():
    ed = Editor("mid")
    a, b = Insert(ed, 0, "<"), Insert(ed, 4, ">")
    a.do()
    b.do()
    assert ed.text == "<mid>", f"Inserting at the start and at the end failed: {ed.text!r}."
    b.undo()
    a.undo()
    assert ed.text == "mid", f"Undoing in reverse order must restore the text, got {ed.text!r}."


def test_delete_remembers_what_it_removed():
    ed = Editor("hello world")
    cmd = Delete(ed, 5, 11)
    cmd.do()
    assert ed.text == "hello", f"Delete(5, 11) must remove ' world', got {ed.text!r}."
    cmd.undo()
    assert ed.text == "hello world", (
        f"Delete.undo must put back the removed text at the same place, got {ed.text!r}. "
        "Save text[start:end] inside do()."
    )


def test_replace_with_different_length():
    ed = Editor("a cat sat")
    cmd = Replace(ed, 2, 5, "elephant")
    cmd.do()
    assert ed.text == "a elephant sat", f"Replace(2, 5, 'elephant') gave {ed.text!r}."
    cmd.undo()
    assert ed.text == "a cat sat", (
        f"Replace.undo gave {ed.text!r}. Remember the OLD text in do() and cut out len(new) characters when undoing."
    )


def test_bad_positions_raise_index_error_and_change_nothing():
    ed = Editor("abc")
    for cmd in (Insert(ed, 4, "x"), Insert(ed, -1, "x"), Delete(ed, 2, 5), Delete(ed, 2, 1), Replace(ed, 0, 9, "z")):
        with pytest.raises(IndexError):
            cmd.do()
        assert ed.text == "abc", f"A failing command must leave the text unchanged, got {ed.text!r}."


def test_history_run_and_undo_all():
    ed, h = Editor(), History()
    h.run(Insert(ed, 0, "hello"))
    h.run(Insert(ed, 5, " world"))
    h.run(Replace(ed, 0, 5, "HELLO"))
    assert ed.text == "HELLO world", f"After three commands the text is 'HELLO world', got {ed.text!r}."
    assert [h.undo(), h.undo()] == [True, True], "undo() returns True when something was undone."
    assert ed.text == "hello", f"Two undos must give 'hello', got {ed.text!r}."
    assert h.undo() is True and ed.text == "", f"The third undo must give '', got {ed.text!r}."


def test_undo_with_nothing_returns_false():
    h = History()
    assert h.undo() is False, "undo() on an empty history returns False (and does not raise)."
    assert h.redo() is False, "redo() with nothing to redo returns False."
    ed = Editor("x")
    h.run(Insert(ed, 1, "y"))
    h.undo()
    assert h.undo() is False and ed.text == "x", "Undoing more times than commands run returns False and changes nothing."


def test_redo_replays_in_order():
    ed, h = Editor(), History()
    h.run(Insert(ed, 0, "a"))
    h.run(Insert(ed, 1, "b"))
    h.run(Insert(ed, 2, "c"))
    h.undo()
    h.undo()
    assert ed.text == "a", f"Expected 'a' after two undos, got {ed.text!r}."
    assert h.redo() is True and ed.text == "ab", f"First redo must bring back 'b': {ed.text!r}."
    assert h.redo() is True and ed.text == "abc", f"Second redo must bring back 'c': {ed.text!r}."
    assert h.redo() is False, "Nothing left to redo."


def test_new_command_clears_redo():
    ed, h = Editor(), History()
    h.run(Insert(ed, 0, "a"))
    h.run(Insert(ed, 1, "b"))
    h.undo()
    h.run(Insert(ed, 1, "X"))
    assert ed.text == "aX", f"Got {ed.text!r}."
    assert h.redo() is False, "Running a new command must clear the redo stack (the old future is gone)."
    assert ed.text == "aX", "A failed redo must not change the text."


def test_redo_of_delete_deletes_again():
    ed, h = Editor("abcdef"), History()
    h.run(Delete(ed, 1, 3))
    h.undo()
    assert ed.text == "abcdef", "Undo of the delete."
    h.redo()
    assert ed.text == "adef", f"Redo of Delete(1, 3) must delete 'bc' again, got {ed.text!r}."
    h.undo()
    assert ed.text == "abcdef", f"A second undo must still restore 'bc': {ed.text!r}."


def test_macro_runs_in_order_and_undoes_in_reverse():
    log = []
    macro = Macro([Fake("a", log), Fake("b", log), Fake("c", log)])
    macro.do()
    macro.undo()
    assert log == ["do a", "do b", "do c", "undo c", "undo b", "undo a"], (
        f"Got {log}. A macro runs its commands in order and undoes them in REVERSE order."
    )


def test_macro_on_a_real_editor_is_one_history_step():
    ed, h = Editor("hello"), History()
    h.run(Macro([Insert(ed, 5, ", world"), Replace(ed, 0, 1, "J"), Delete(ed, 4, 5)]))
    assert ed.text == "Jell, world", f"Macro result wrong: {ed.text!r}."
    assert h.undo() is True and ed.text == "hello", (
        f"One undo must revert the whole macro, got {ed.text!r}. If your undo order is wrong the positions drift."
    )
    assert h.undo() is False, "The macro was a single history entry."
    h.redo()
    assert ed.text == "Jell, world", f"Redo must replay the whole macro, got {ed.text!r}."


def test_macros_can_nest():
    ed = Editor("")
    inner = Macro([Insert(ed, 1, "b"), Insert(ed, 2, "c")])
    outer = Macro([Insert(ed, 0, "a"), inner, Insert(ed, 3, "d")])
    outer.do()
    assert ed.text == "abcd", f"Nested macro gave {ed.text!r}."
    outer.undo()
    assert ed.text == "", f"Undo of a nested macro gave {ed.text!r}."


def test_failing_macro_is_atomic_and_not_recorded():
    ed, h = Editor("abc"), History()
    macro = Macro([Insert(ed, 0, ">"), Delete(ed, 1, 2), Insert(ed, 99, "!")])
    with pytest.raises(IndexError):
        h.run(macro)
    assert ed.text == "abc", (
        f"Got {ed.text!r}. When a step fails, a macro must undo the steps it already did (in reverse) and re-raise."
    )
    assert h.undo() is False, "A command that raised must not be recorded in the history."

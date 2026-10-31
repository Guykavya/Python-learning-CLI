from solution import Counter, HistoryMixin, TextBox


def test_mixin_has_no_init_and_no_shared_list():
    assert "__init__" not in vars(HistoryMixin), "HistoryMixin must not define __init__; create _history lazily in _log."
    assert "_history" not in vars(HistoryMixin), (
        "Do not put `_history = []` in the class body: one list would be shared by every object. "
        "Create self._history the first time _log runs."
    )
    assert HistoryMixin.max_history is None, "max_history is a class attribute that defaults to None (no limit)."


def test_empty_history_does_not_crash():
    assert Counter().history() == [], "history() on an object that logged nothing returns []; it must not raise AttributeError."
    assert TextBox().history() == [], "Same for a TextBox."


def test_counter():
    c = Counter(10)
    assert c.value == 10, "Counter(10) starts at 10."
    c.increment()
    c.increment(5)
    assert c.value == 16, "10 + 1 + 5 = 16."
    c.reset()
    assert c.value == 0, "reset() sets value to 0."
    assert c.history() == ["increment(1)", "increment(5)", "reset()"], (
        "Each action logs 'name(args)'; increment() with no argument logs its default, increment(1)."
    )


def test_counters_have_separate_histories():
    a = Counter()
    b = Counter()
    a.increment()
    assert b.history() == [], "One counter's actions appeared in another's history: the list must belong to each object."


def test_textbox_text():
    t = TextBox()
    t.type("hello")
    t.backspace(2)
    assert t.text == "hel", "backspace(2) removes the last 2 characters."
    t.backspace()
    assert t.text == "he", "backspace() removes 1 character by default."
    t.backspace(10)
    assert t.text == "", "Removing more characters than the text has leaves an empty text, not an error."
    t.type("hello")
    t.backspace(7)
    assert t.text == "", (
        "backspace(7) on 'hello' must leave ''. Careful: 'hello'[:5 - 7] is 'hello'[:-2], which is 'hel'."
    )
    t.type("x")
    t.clear()
    assert t.text == "", "clear() empties the text."


def test_textbox_entries_use_repr():
    t = TextBox()
    t.type("hello")
    t.backspace(2)
    assert t.history() == ["type('hello')", "backspace(2)"], "Write each argument with repr(): strings get quotes."


def test_textbox_keeps_only_five():
    t = TextBox()
    t.type("hello")
    t.backspace(2)
    for ch in "abcd":
        t.type(ch)
    assert t.history() == ["backspace(2)", "type('a')", "type('b')", "type('c')", "type('d')"], (
        "TextBox sets max_history = 5: drop the OLDEST entries so only the newest 5 stay."
    )
    assert TextBox.max_history == 5, "Set max_history = 5 as a class attribute of TextBox."
    assert Counter.max_history is None, "Counter keeps the mixin's default: no limit."


def test_counter_has_no_limit():
    c = Counter()
    for _ in range(20):
        c.increment()
    assert len(c.history()) == 20, "With max_history = None nothing is dropped."


def test_history_returns_a_copy():
    c = Counter()
    c.increment()
    h = c.history()
    h.append("fake()")
    assert c.history() == ["increment(1)"], "history() must return a new list, so the caller cannot change the log."


def test_clear_history():
    c = Counter()
    c.increment()
    c.clear_history()
    assert c.history() == [], "clear_history() empties the log."
    c.increment(3)
    assert c.history() == ["increment(3)"], "Logging works again after clearing."


def test_mixin_works_with_any_class():
    class Lamp(HistoryMixin):
        def __init__(self):
            self.on = False

        def toggle(self):
            self.on = not self.on
            self._log("toggle")

        def dim(self, level, smooth):
            self._log("dim", level, smooth)

    lamp = Lamp()
    lamp.toggle()
    lamp.dim(30, True)
    assert lamp.history() == ["toggle()", "dim(30, True)"], (
        "The mixin must work in any class. Several arguments are joined with ', '."
    )

import ast
import inspect
from datetime import datetime, timedelta
from pathlib import Path

import solution
from solution import is_expired, make_greeting, pick_tip, save_report


class FakeFile:
    def __init__(self):
        self.parts = []
        self.closed = False

    def write(self, text):
        self.parts.append(text)
        return len(text)

    def writelines(self, lines):
        self.parts.extend(lines)

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class FakeOpener:
    def __init__(self):
        self.calls = []
        self.file = FakeFile()

    def __call__(self, path, mode="r", *args, **kwargs):
        self.calls.append((path, mode))
        return self.file


class FakeRandom:
    def __init__(self, index):
        self.index = index
        self.seen = []

    def choice(self, seq):
        self.seen.append(list(seq))
        return seq[self.index]


def at(hour):
    return lambda: datetime(2024, 5, 17, hour, 30)


def function_source(name):
    tree = ast.parse(Path(solution.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def test_greeting_uses_the_injected_clock():
    assert make_greeting("Ana", now=at(9)) == "Good morning, Ana", (
        "At 09:30 the greeting must be 'Good morning, Ana'. Call the injected now() instead of datetime.now()."
    )
    assert make_greeting("Ana", now=at(14)) == "Good afternoon, Ana", "14:30 is afternoon."
    assert make_greeting("Ana", now=at(21)) == "Good evening, Ana", "21:30 is evening."


def test_greeting_boundaries():
    assert make_greeting("Bo", now=at(0)) == "Good morning, Bo", "Hour 0 is morning."
    assert make_greeting("Bo", now=at(11)) == "Good morning, Bo", "Hour 11 is still morning."
    assert make_greeting("Bo", now=at(12)) == "Good afternoon, Bo", "Hour 12 starts the afternoon."
    assert make_greeting("Bo", now=at(17)) == "Good afternoon, Bo", "Hour 17 is still afternoon."
    assert make_greeting("Bo", now=at(18)) == "Good evening, Bo", "Hour 18 starts the evening."


def test_expiry_with_a_fake_clock():
    token = {"expires": datetime(2024, 5, 17, 12, 0)}
    before = lambda: datetime(2024, 5, 17, 11, 59, 59)
    exactly = lambda: datetime(2024, 5, 17, 12, 0)
    after = lambda: datetime(2024, 5, 17, 12, 0, 1)
    assert is_expired(token, now=before) is False, "One second before 'expires' the token is still valid."
    assert is_expired(token, now=exactly) is True, "At exactly 'expires' the token is expired (>=)."
    assert is_expired(token, now=after) is True, "After 'expires' the token is expired."


def test_clock_is_called_each_time_not_stored():
    ticks = iter([datetime(2024, 1, 1), datetime(2030, 1, 1)])
    token = {"expires": datetime(2025, 1, 1)}
    clock = lambda: next(ticks)
    assert is_expired(token, now=clock) is False, "First call: 2024 is before 2025."
    assert is_expired(token, now=clock) is True, (
        "Second call: the clock moved to 2030. Call now() inside the function every time."
    )


def test_pick_tip_uses_the_injected_rng():
    tips = ["a", "b", "c"]
    rng = FakeRandom(2)
    assert pick_tip(tips, rng=rng) == "c", "pick_tip must return whatever rng.choice returns."
    assert rng.seen == [tips], "Call rng.choice(tips) exactly once with the list you were given."


def test_save_report_uses_the_injected_opener():
    opener = FakeOpener()
    save_report([("ana", 90), ("bo", 75)], "/tmp/out.csv", opener=opener)
    assert opener.calls == [("/tmp/out.csv", "w")], (
        f"Expected one opener('/tmp/out.csv', 'w') call, got {opener.calls}. Use the injected opener, not open()."
    )
    assert "".join(opener.file.parts) == "ana,90\nbo,75\n", (
        f"Wrong file content {''.join(opener.file.parts)!r}. One 'name,score' line per row, each ending in a newline."
    )
    assert opener.file.closed, "The file must be closed: use 'with opener(path, \"w\") as f:'."


def test_save_report_empty_rows_still_creates_file():
    opener = FakeOpener()
    save_report([], "empty.csv", opener=opener)
    assert opener.calls == [("empty.csv", "w")], "Even with no rows the file must be opened (and so created)."
    assert "".join(opener.file.parts) == "", "No rows means no content."


def test_defaults_still_use_the_real_things(tmp_path):
    assert make_greeting("Ana").endswith(", Ana") and make_greeting("Ana").startswith("Good "), (
        "Without 'now' the function must still work using the real clock."
    )
    future = {"expires": datetime.now() + timedelta(days=1)}
    past = {"expires": datetime.now() - timedelta(days=1)}
    assert is_expired(future) is False and is_expired(past) is True, "Default 'now' must be the real clock."
    assert pick_tip(["only"]) == "only", "Default 'rng' must be the real random module."
    target = tmp_path / "r.csv"
    save_report([("x", 1)], str(target))
    assert target.read_text() == "x,1\n", "Default 'opener' must be the real open()."


def test_no_hidden_collaborators_in_the_bodies():
    for name in ("make_greeting", "is_expired", "pick_tip", "save_report"):
        node = function_source(name)
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and sub.func.attr == "now" \
                    and isinstance(sub.func.value, ast.Name) and sub.func.value.id == "datetime":
                raise AssertionError(f"{name} calls datetime.now() directly. Take a 'now' parameter and call it.")
            if isinstance(sub, ast.Attribute) and isinstance(sub.value, ast.Name) and sub.value.id == "random":
                raise AssertionError(f"{name} uses the random module directly. Take an 'rng' parameter.")
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == "open":
                raise AssertionError(f"{name} calls open() directly. Take an 'opener' parameter.")


def test_parameters_have_the_agreed_names():
    assert "now" in inspect.signature(make_greeting).parameters, "make_greeting needs a 'now' parameter."
    assert "now" in inspect.signature(is_expired).parameters, "is_expired needs a 'now' parameter."
    assert "rng" in inspect.signature(pick_tip).parameters, "pick_tip needs an 'rng' parameter."
    assert "opener" in inspect.signature(save_report).parameters, "save_report needs an 'opener' parameter."

import ast
from pathlib import Path

import solution
from solution import copy_text, format_with_precision, read_all, run_locked, temp_setting

TREE = ast.parse(Path(solution.__file__).read_text())


class Resource:
    def __init__(self, name, data="", fail_read=False):
        self.name, self.data, self.fail_read = name, data, fail_read
        self.closed = 0
        self.written = ""

    def read(self):
        if self.fail_read:
            raise OSError("read failed")
        return self.data

    def write(self, text):
        self.written += text

    def close(self):
        self.closed += 1

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class Opener:
    def __init__(self, data=None, fail_read=(), fail_open=()):
        self.data, self.fail_read, self.fail_open = data or {}, fail_read, fail_open
        self.made = []

    def __call__(self, name):
        if name in self.fail_open:
            raise FileNotFoundError(name)
        r = Resource(name, self.data.get(name, ""), fail_read=name in self.fail_read)
        self.made.append(r)
        return r


class Lock:
    def __init__(self):
        self.held = False
        self.acquired = 0
        self.released = 0

    def acquire(self):
        self.held = True
        self.acquired += 1

    def release(self):
        self.held = False
        self.released += 1

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()
        return False


class Cfg:
    def __init__(self):
        self.precision = 6

    def fmt(self, n):
        if n < 0:
            raise ValueError("negative")
        return f"{n:.{self.precision}f}"


def _func(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def test_read_all():
    op = Opener({"a": "hello"})
    assert read_all(op, "a") == "hello", "Return what read() gives."
    assert [r.closed for r in op.made] == [1], "The resource must be closed exactly once."


def test_read_all_closes_on_error():
    op = Opener({"a": "x"}, fail_read={"a"})
    try:
        read_all(op, "a")
    except OSError:
        pass
    else:
        raise AssertionError("The OSError from read() must reach the caller.")
    assert [r.closed for r in op.made] == [1], "Close even when read() fails: that is what 'with' guarantees."


def test_copy_text():
    op = Opener({"s": "data"})
    assert copy_text(op, "s", "d") == 4, "Return the number of characters copied."
    s, d = op.made
    assert d.written == "data", "dst must receive the text of src."
    assert (s.closed, d.closed) == (1, 1), "Both resources closed exactly once."


def test_copy_text_closes_both_when_read_fails():
    op = Opener({"s": "x"}, fail_read={"s"})
    try:
        copy_text(op, "s", "d")
    except OSError:
        pass
    assert [r.closed for r in op.made] == [1, 1], "If reading fails, src AND dst must still be closed."


def test_copy_text_closes_src_when_dst_cannot_open():
    op = Opener({"s": "x"}, fail_open={"d"})
    try:
        copy_text(op, "s", "d")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("The FileNotFoundError from opening dst must reach the caller.")
    assert [r.closed for r in op.made] == [1], "src was opened before dst failed: it must still be closed."


def test_run_locked():
    lock = Lock()
    assert run_locked(lock, lambda: 42) == 42, "Return func()'s result."
    assert (lock.acquired, lock.released, lock.held) == (1, 1, False), "Acquire once, release once."


def test_run_locked_releases_on_error():
    lock = Lock()

    def boom():
        assert lock.held, "The lock must be held while func runs."
        raise KeyError("x")

    try:
        run_locked(lock, boom)
    except KeyError:
        pass
    else:
        raise AssertionError("The error from func must reach the caller.")
    assert lock.held is False and lock.released == 1, "Release the lock even when func raises."


def test_temp_setting():
    class Obj:
        pass

    o = Obj()
    o.x = 1
    with temp_setting(o, "x", 5):
        assert o.x == 5, "Inside the with block the setting has the temporary value."
    assert o.x == 1, "After the block the old value must be back."


def test_temp_setting_restores_on_error():
    class Obj:
        pass

    o = Obj()
    o.x = 1
    try:
        with temp_setting(o, "x", 5):
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    else:
        raise AssertionError("temp_setting must not swallow exceptions.")
    assert o.x == 1, "Restore the old value even when the block raises (try/finally around yield)."


def test_temp_setting_new_attribute_and_nesting():
    class Obj:
        pass

    o = Obj()
    with temp_setting(o, "y", 1):
        assert o.y == 1, "The attribute is set inside."
    assert not hasattr(o, "y"), "An attribute that did not exist before must be removed again."
    o.z = 0
    with temp_setting(o, "z", 1):
        with temp_setting(o, "z", 2):
            assert o.z == 2, "Inner value wins."
        assert o.z == 1, "Inner block restores the outer temporary value."
    assert o.z == 0, "Outer block restores the original."


def test_format_with_precision():
    cfg = Cfg()
    assert format_with_precision(cfg, [3.14159, 2.71828], 2) == ["3.14", "2.72"], "Format with the temporary precision."
    assert cfg.precision == 6, "The original precision (6) must be restored."


def test_format_with_precision_restores_on_error():
    cfg = Cfg()
    try:
        format_with_precision(cfg, [1.0, -1.0], 1)
    except ValueError:
        pass
    else:
        raise AssertionError("The ValueError from fmt must reach the caller.")
    assert cfg.precision == 6, "Restore the precision even when formatting fails."


def test_structure_with_not_try():
    for name in ("read_all", "copy_text", "run_locked", "format_with_precision"):
        f = _func(name)
        assert any(isinstance(n, ast.With) for n in ast.walk(f)), f"{name} should use a 'with' statement."
        assert not any(isinstance(n, ast.Try) for n in ast.walk(f)), (
            f"{name} still has try/finally. Move the cleanup into a context manager and use 'with'."
        )


def test_copy_text_single_with():
    withs = [n for n in ast.walk(_func("copy_text")) if isinstance(n, ast.With)]
    assert len(withs) == 1 and len(withs[0].items) == 2, (
        "copy_text: open both resources in ONE with statement: 'with a(...) as s, b(...) as d:' (no deep nesting)."
    )


def test_format_uses_temp_setting():
    calls = [n for n in ast.walk(_func("format_with_precision"))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "temp_setting"]
    assert calls, "format_with_precision should use your temp_setting helper instead of saving and restoring by hand."

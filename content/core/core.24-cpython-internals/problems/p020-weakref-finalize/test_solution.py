import gc
import weakref

import pytest

from solution import TempResource, live_resources

# CPython frees an object as soon as its last reference goes. gc.collect() is called anyway before
# every "is it freed?" check, so the tests do not depend on that detail.


def test_open_is_logged():
    log = []
    r = TempResource("t-open", log)
    assert log == ["open t-open"], "Creating a resource appends 'open <name>'."
    assert r.closed is False, "A new resource is not closed."


def test_collected_resource_is_closed():
    log = []
    r = TempResource("t-gc", log)
    del r
    gc.collect()
    assert log == ["open t-gc", "close t-gc"], (
        "When the last reference goes, the resource must be cleaned up: register "
        "weakref.finalize(self, callback, name, log) in __init__."
    )


def test_object_is_really_freed():
    log = []
    r = TempResource("t-free", log)
    ref = weakref.ref(r)
    del r
    gc.collect()
    assert ref() is None, (
        "The object is still alive after del + gc.collect(). The finalizer holds its callback and arguments "
        "STRONGLY: if you pass a bound method (self.something) or self in the args, it keeps the object alive "
        "forever. Use a plain function that receives only the name and the log."
    )


def test_close_runs_once():
    log = []
    r = TempResource("t-once", log)
    r.close()
    r.close()
    assert log == ["open t-once", "close t-once"], "close() twice must log 'close' only once."
    assert r.closed is True
    del r
    gc.collect()
    assert log.count("close t-once") == 1, "A resource closed by hand must not be closed again when it is collected."


def test_closed_is_read_only():
    r = TempResource("t-ro", [])
    with pytest.raises(AttributeError):
        r.closed = True


def test_with_block():
    log = []
    with TempResource("t-with", log) as r:
        assert isinstance(r, TempResource), "__enter__ must return the resource itself."
        assert not r.closed
    assert r.closed, "Leaving the with block must close the resource."
    assert log == ["open t-with", "close t-with"]


def test_with_block_on_error():
    log = []
    with pytest.raises(ValueError):
        with TempResource("t-err", log):
            raise ValueError("boom")
    assert log == ["open t-err", "close t-err"], (
        "The resource must be closed even when the block raises, and the exception must not be swallowed "
        "(__exit__ returns False)."
    )


def test_cycle_is_cleaned_by_gc():
    log = []
    r = TempResource("t-cycle", log)
    r.me = r                      # a reference cycle: reference counting alone cannot free it
    del r
    gc.collect()
    assert "close t-cycle" in log, "After gc.collect() the cycle is freed, so the finalizer must run."


def test_live_resources():
    a = TempResource("live-a", [])
    b = TempResource("live-b", [])
    c = TempResource("live-c", [])
    live = live_resources()
    assert {"live-a", "live-b", "live-c"} <= set(live), "Existing, open resources are listed."
    assert live == sorted(live), "Return the names sorted."
    c.close()
    del a
    gc.collect()
    live = live_resources()
    assert "live-b" in live, "b still exists and is open."
    assert "live-a" not in live, (
        "a was deleted. Track instances in a weakref.WeakSet, not a list or set (which would keep them alive)."
    )
    assert "live-c" not in live, "c still exists but is closed, so it is not listed."
    del b, c


def test_live_resources_do_not_keep_objects_alive():
    r = TempResource("live-keep", [])
    ref = weakref.ref(r)
    live_resources()
    del r
    gc.collect()
    assert ref() is None, "Registering in live_resources must not keep the resource alive (use a WeakSet)."

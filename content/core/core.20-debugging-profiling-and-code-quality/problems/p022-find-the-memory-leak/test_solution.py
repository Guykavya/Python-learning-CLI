import gc
import tracemalloc
import weakref

import pytest

import solution
from solution import EventBus, Widget, cache_size, clear_cache, parse_record, stats


@pytest.fixture(autouse=True)
def fresh_cache():
    clear_cache()
    yield
    clear_cache()


def line(i):
    return f"user{i}, {i % 90}, Pune"


# ---------- the cache ----------

def test_parse_still_works():
    assert parse_record("alice, 30, Paris") == ("alice", 30, "Paris"), "parse_record must still split on commas, strip, and turn the age into an int."


def test_repeats_come_from_cache():
    for _ in range(50):
        parse_record("bob, 41, Delhi")
    assert stats["computed"] == 1, f"50 identical lines were parsed {stats['computed']} times. A repeated line must be answered from the cache."


def test_cache_is_bounded():
    for i in range(5000):
        parse_record(line(i))
    assert cache_size() <= solution.MAX_CACHE, (
        f"After 5000 different lines the cache holds {cache_size()} entries. It must never hold more than "
        "MAX_CACHE (1000): this is the first leak, a module-level dict that only grows."
    )
    assert cache_size() == solution.MAX_CACHE, f"cache_size() is {cache_size()}. Keep the cache FULL (1000), only drop one entry per new line."


def test_least_recently_used_is_dropped():
    for i in range(1000):
        parse_record(line(i))
    parse_record(line(0))          # line 0 is used again, so line 1 is now the oldest
    parse_record(line(1000))       # cache is full: one line must go
    before = stats["computed"]
    parse_record(line(0))
    assert stats["computed"] == before, (
        "Line 0 was used just before the cache filled up, so it must still be cached. Drop the LEAST RECENTLY "
        "used line (move a line to the end when it is used), not simply the first one ever added."
    )
    parse_record(line(1))
    assert stats["computed"] == before + 1, "Line 1 was the least recently used line, so it should have been dropped and parsed again."


def test_clear_cache_resets_everything():
    for i in range(10):
        parse_record(line(i))
    clear_cache()
    assert cache_size() == 0 and stats["computed"] == 0, "clear_cache() must empty the cache and set stats['computed'] back to 0."
    parse_record(line(1))
    assert stats["computed"] == 1, "After clear_cache() a line must be parsed again."


def test_memory_stays_bounded():
    for i in range(2000):
        parse_record(line(i))  # warm up: cache already full
    tracemalloc.start()
    try:
        start, _ = tracemalloc.get_traced_memory()
        for i in range(2000, 22000):
            parse_record(line(i))
        end, _ = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    grown = end - start
    assert grown < 500_000, (
        f"Memory grew by {grown:,} bytes while parsing 20,000 new lines into an already full cache. "
        "A bounded cache should stay about the same size."
    )


# ---------- the listeners ----------

def test_closed_widgets_leave_the_bus():
    bus = EventBus()
    for _ in range(1000):
        Widget(bus).close()
    assert bus.handler_count() == 0, (
        f"The bus still holds {bus.handler_count()} handlers after every widget closed. This is the second leak: "
        "Widget.close() must call self.bus.unsubscribe(self.on_event), and unsubscribe must remove it."
    )


def test_closed_widget_is_garbage_collected():
    bus = EventBus()
    w = Widget(bus)
    ref = weakref.ref(w)
    w.close()
    del w
    gc.collect()
    assert ref() is None, (
        "A closed widget is still alive. The bus keeps the bound method w.on_event, and a bound method keeps its "
        "object (w) alive. Remove it from the bus in close()."
    )


def test_open_widgets_still_receive_events():
    bus = EventBus()
    a, b = Widget(bus), Widget(bus)
    bus.publish("hello")
    b.close()
    bus.publish("again")
    assert a.seen == ["hello", "again"], f"An open widget must get every event, got {a.seen}."
    assert b.seen == [], f"A closed widget must not receive events any more, got {b.seen}."


def test_unsubscribe_unknown_and_double_close():
    bus = EventBus()
    w = Widget(bus)
    bus.unsubscribe(print)  # never subscribed
    w.close()
    w.close()
    assert bus.handler_count() == 0, "unsubscribe of an unknown handler and a second close() must do nothing (no ValueError)."


def test_unsubscribe_plain_function():
    bus = EventBus()
    got = []
    handler = got.append
    bus.subscribe(handler)
    bus.unsubscribe(handler)
    bus.publish(1)
    assert got == [] and bus.handler_count() == 0, "unsubscribe(handler) must remove that handler from the bus."


def test_close_during_publish():
    bus = EventBus()
    received = []

    class SelfClosing(Widget):
        def on_event(self, event):
            received.append(("self-closing", event))
            self.close()

    SelfClosing(bus)
    last = Widget(bus)
    bus.publish("ping")
    assert last.seen == ["ping"], (
        f"The widget after the self-closing one got {last.seen}. Removing an item from a list while a for loop walks "
        "over it makes the loop skip the next item. Loop over a copy: for h in list(self._handlers)."
    )
    assert bus.handler_count() == 1, "Only the self-closing widget should have left the bus."

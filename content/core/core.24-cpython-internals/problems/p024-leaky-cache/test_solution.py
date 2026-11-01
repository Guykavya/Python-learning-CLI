import gc
import weakref

import pytest

from solution import Document, EventBus, cache_size, describe, log, stats


class Window:
    def __init__(self, name):
        self.name = name
        self.seen = []

    def on_save(self, event):
        self.seen.append(event)


class Thing:
    def __init__(self):
        self.a = 1
        self.b = 2


# ---------------------------------------------------------------- bug 1: subscribers kept alive

def test_bound_method_subscriber_still_receives_events():
    bus = EventBus()
    w = Window("main")
    bus.subscribe(w.on_save)
    bus.publish("saved")
    assert w.seen == ["saved"], "A live subscriber must still get every published event."


def test_bug1_closed_window_is_freed():
    bus = EventBus()
    w = Window("temp")
    bus.subscribe(w.on_save)
    ref = weakref.ref(w)
    del w
    gc.collect()
    assert ref() is None, (
        "Bug 1: the window is still alive after its last reference was deleted. The bus stores the bound "
        "method w.on_save, and a bound method holds w (its __self__). Store weakref.WeakMethod(callback) "
        "for bound methods."
    )


def test_bug1_dead_subscribers_are_dropped():
    bus = EventBus()
    w = Window("temp")
    bus.subscribe(w.on_save)
    del w
    gc.collect()
    bus.publish("after close")          # must not crash on the dead subscriber
    assert bus.subscriber_count() == 0, (
        "When a subscriber's object has died, publish/subscriber_count must skip and drop it (the WeakMethod "
        "returns None)."
    )


def test_functions_and_lambdas_stay_subscribed():
    bus = EventBus()
    got = []

    def handler(event):
        got.append(("handler", event))

    bus.subscribe(handler)
    bus.subscribe(lambda event: got.append(("lambda", event)))
    gc.collect()
    bus.publish("e")
    assert got == [("handler", "e"), ("lambda", "e")], (
        "Plain functions and lambdas must be kept STRONGLY: a lambda has no other reference, so a weak "
        "reference to it would die at once. Use WeakMethod only for bound methods (inspect.ismethod)."
    )
    assert bus.subscriber_count() == 2


def test_builtin_method_subscriber():
    bus = EventBus()
    got = []
    bus.subscribe(got.append)          # a method of a C type: not an inspect.ismethod method
    bus.publish(1)
    assert got == [1], (
        "got.append is a builtin method. weakref.WeakMethod rejects it (TypeError), and lists cannot be "
        "weakly referenced anyway: keep it strongly."
    )


def test_unsubscribe_bound_method():
    bus = EventBus()
    w = Window("main")
    bus.subscribe(w.on_save)
    bus.unsubscribe(w.on_save)          # a NEW bound method object, equal to the stored one
    bus.publish("x")
    assert w.seen == [] and bus.subscriber_count() == 0, (
        "unsubscribe must still work after the fix. A WeakMethod is not == the bound method; compare "
        "ref() == callback instead."
    )


def test_unsubscribe_function_and_missing():
    bus = EventBus()

    def handler(event):
        pass

    bus.subscribe(handler)
    bus.unsubscribe(handler)
    assert bus.subscriber_count() == 0
    with pytest.raises(ValueError):
        bus.unsubscribe(handler)


# ---------------------------------------------------------------- bug 2: the page/document cycle

def test_bug2_document_freed_without_waiting_for_gc():
    log.clear()
    gc.disable()                        # only reference counting may free it in this test
    try:
        doc = Document("report")
        doc.add_page()
        doc.add_page()
        del doc
        freed_at_once = "freed report" in log
    finally:
        gc.enable()
        gc.collect()
    assert freed_at_once, (
        "Bug 2: deleting the last reference did not free the document. doc.pages holds each Page and "
        "page.document holds doc: a reference cycle, which only the (unpredictable) cyclic garbage "
        "collector can free. Make the back-reference weak: weakref.ref(document)."
    )


def test_page_document_works_while_alive():
    doc = Document("live")
    page = doc.add_page()
    assert page.document is doc, "page.document must still return the document (a property over the weakref)."
    assert doc.pages == [page]


def test_page_outliving_document_sees_none():
    log.clear()
    doc = Document("gone")
    page = doc.add_page()
    del doc
    gc.collect()
    assert "freed gone" in log, "A page must not keep its document alive."
    assert page.document is None, "Once the document is freed, page.document is None (the weakref is dead)."


# ---------------------------------------------------------------- bug 3: the cache keeps objects alive

def test_describe_caches():
    t = Thing()
    before = stats["computed"]
    first = describe(t)
    second = describe(t)
    assert first == "Thing with 2 attributes" and second == first
    assert stats["computed"] == before + 1, "The summary must be computed once per object, then cached."


def test_bug3_described_object_is_freed():
    t = Thing()
    describe(t)
    ref = weakref.ref(t)
    del t
    gc.collect()
    assert ref() is None, (
        "Bug 3: an object stays alive forever once describe() has seen it, because it is a key of a plain "
        "dict. Use weakref.WeakKeyDictionary, whose entries disappear with their key."
    )


def test_bug3_cache_shrinks_back():
    gc.collect()
    before = cache_size()
    things = [Thing() for _ in range(5)]
    for t in things:
        describe(t)
    assert cache_size() == before + 5, "Five live objects, five cache entries."
    del things, t
    gc.collect()
    assert cache_size() == before, (
        "After the objects are freed their entries must be gone too. Keying a dict by id(obj) frees the "
        "objects but leaves stale entries (and a new object may reuse an old id and get a wrong summary)."
    )

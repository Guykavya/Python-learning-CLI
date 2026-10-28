from collections import Counter

import pytest

from solution import Document, Note, OwnerMixin, Photo, SharedDocument, TimestampMixin

ALL = (TimestampMixin, OwnerMixin, Document, SharedDocument, Photo, Note)


def make(cls, *args, **kwargs):
    """Create an object; turn an unexpected TypeError into a clear test failure."""
    try:
        return cls(*args, **kwargs)
    except TypeError as e:
        pytest.fail(
            f"{cls.__name__}(...) raised TypeError: {e}. Does every __init__ pass the other keywords on "
            "with super().__init__(**kwargs)? A super().__init__() without **kwargs loses them."
        )


def expect_type_error(func, why):
    try:
        func()
    except TypeError:
        return
    pytest.fail(why)


@pytest.fixture
def calls(monkeypatch):
    """Wrap every __init__ so the test can count how often each one runs."""
    counter = Counter()
    for cls in ALL:
        original = vars(cls).get("__init__")
        assert original is not None, f"{cls.__name__} must define its own __init__."

        def wrapper(self, *args, __original=original, __name=cls.__name__, **kwargs):
            counter[__name] += 1
            __original(self, *args, **kwargs)

        monkeypatch.setattr(cls, "__init__", wrapper)
    return counter


def test_mro_order():
    names = [c.__name__ for c in Document.__mro__]
    assert names == ["Document", "TimestampMixin", "OwnerMixin", "object"], (
        "Document must inherit from (TimestampMixin, OwnerMixin), in that order."
    )


def test_document_attributes():
    d = make(Document, "Plan", owner="Kavya", created=3)
    assert (d.title, d.owner, d.created, d.updated) == ("Plan", "Kavya", 3, 3), (
        "Every __init__ in the MRO must run: Document sets title, TimestampMixin sets created/updated, "
        "OwnerMixin sets owner. Did a mixin forget to call super().__init__(**kwargs)?"
    )


def test_every_init_runs_once(calls):
    make(Document, "Plan", owner="Kavya", created=3)
    assert calls == Counter({"Document": 1, "TimestampMixin": 1, "OwnerMixin": 1}), (
        f"Each __init__ in the MRO must run exactly once, got {dict(calls)}. "
        "Use super().__init__(**kwargs) everywhere, never TimestampMixin.__init__(self, ...)."
    )


def test_shared_document_chain(calls):
    s = make(SharedDocument, "Notes", owner="Ravi", readers=["Asha"], created=1)
    assert (s.title, s.owner, s.created, s.readers) == ("Notes", "Ravi", 1, ["Asha"]), (
        "SharedDocument passes title and the rest to Document via super().__init__(title, **kwargs)."
    )
    assert calls == Counter({"SharedDocument": 1, "Document": 1, "TimestampMixin": 1, "OwnerMixin": 1}), (
        f"Four __init__ methods, each once. Got {dict(calls)}."
    )


def test_readers_not_shared():
    names = ["Asha"]
    a = make(SharedDocument, "A", owner="R", readers=names)
    b = make(SharedDocument, "B", owner="R")
    a.readers.append("Ben")
    assert names == ["Asha"], "Copy the readers with list(readers); do not keep the caller's list."
    assert b.readers == [], "Each object needs its own new list."


def test_default_created():
    d = make(Document, "Plan", owner="Kavya")
    assert (d.created, d.updated) == (0, 0), "created defaults to 0, and updated starts equal to created."


def test_single_mixin_classes(calls):
    n = make(Note, "buy milk", created=2)
    p = make(Photo, "cat.jpg", owner="Asha")
    assert (n.text, n.created) == ("buy milk", 2), "Note uses only TimestampMixin."
    assert (p.path, p.owner) == ("cat.jpg", "Asha"), "Photo uses only OwnerMixin."
    assert calls == Counter({"Note": 1, "TimestampMixin": 1, "Photo": 1, "OwnerMixin": 1}), (
        f"Each __init__ once per object. Got {dict(calls)}."
    )


def test_owner_is_required():
    expect_type_error(lambda: Document("Plan"), "owner is required: write it as a keyword-only argument without a default (*, owner).")
    expect_type_error(lambda: Photo("cat.jpg"), "Photo needs owner too: it comes from OwnerMixin.")


@pytest.mark.parametrize("bad", ["", None, 42])
def test_owner_validated(bad):
    with pytest.raises(ValueError, match="owner must be a non-empty string"):
        Document("Plan", owner=bad)


def test_unknown_keyword_reaches_object():
    expect_type_error(
        lambda: Document("Plan", owner="Kavya", colour="red"),
        "An unknown keyword must travel down the chain until object.__init__ raises TypeError. "
        "Every __init__, the mixins too, must end with super().__init__(**kwargs).",
    )
    expect_type_error(
        lambda: Note("x", owner="Kavya"),
        "Note has no OwnerMixin, so owner is unknown for a Note. TimestampMixin must forward it with "
        "super().__init__(**kwargs) so that object.__init__ raises TypeError.",
    )


def test_mixins_do_not_swallow_kwargs():
    # A mixin that "eats" all kwargs would hide the typo instead of raising.
    expect_type_error(
        lambda: Photo("cat.jpg", owner="Asha", creatd=5),
        "The typo creatd=5 must reach object.__init__ and raise TypeError. Do not drop leftover keywords.",
    )


def test_touch():
    d = make(Document, "Plan", owner="Kavya", created=3)
    d.touch(5)
    assert d.updated == 5, "touch(day) sets updated."
    with pytest.raises(ValueError, match="cannot update before creation"):
        d.touch(2)
    assert d.updated == 5, "A failed touch must not change updated."


def test_is_owned_by_and_describe():
    d = make(Document, "Plan", owner="Kavya", created=3)
    assert d.is_owned_by("Kavya") is True and d.is_owned_by("Ravi") is False, "is_owned_by compares with owner."
    assert d.describe() == "'Plan' by Kavya, created day 3", "Use f\"{self.title!r} by {self.owner}, created day {self.created}\"."

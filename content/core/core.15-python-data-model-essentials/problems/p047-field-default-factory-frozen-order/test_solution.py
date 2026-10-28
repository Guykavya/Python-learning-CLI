import dataclasses

import pytest

from solution import Playlist, Version


def test_playlist_songs_default_is_a_fresh_list():
    a, b = Playlist("rock"), Playlist("jazz")
    assert a.songs == [], "songs defaults to an empty list."
    a.songs.append("x")
    assert b.songs == [], "Each Playlist needs its OWN list: use field(default_factory=list). A plain `= []` is rejected by dataclass for exactly this reason."


def test_playlist_keeps_given_list():
    mine = ["a"]
    p = Playlist("p", mine)
    assert p.songs is mine, "A list passed in is stored as it is (default_factory only runs when nothing is passed)."


def test_playlist_plays_hidden_from_repr_and_eq():
    p = Playlist("p", ["a"], plays=5)
    assert p.plays == 5, "plays is a normal field with default 0 and can be passed by keyword."
    assert repr(p) == "Playlist(name='p', songs=['a'])", "plays must not appear in repr: field(repr=False)."
    assert Playlist("p", ["a"], plays=1) == Playlist("p", ["a"], plays=99), "plays must be ignored by == : field(compare=False)."
    assert Playlist("p", ["a"]) != Playlist("p", ["b"]), "name and songs are still compared."


def test_playlist_default_plays():
    assert Playlist("p").plays == 0, "plays defaults to 0."


def test_version_ordering():
    assert Version(1, 2, 3) < Version(1, 10, 0), "order=True compares fields in order: 1.2.3 < 1.10.0 because 2 < 10 (numbers, not text)."
    assert Version(2) > Version(1, 99, 99), "Compare major first."
    assert Version(1, 0, 0) <= Version(1) and Version(1, 0, 1) >= Version(1), "<= and >= are generated too."
    assert sorted([Version(1, 5), Version(1, 0, 9), Version(0, 9)]) == [Version(0, 9), Version(1, 0, 9), Version(1, 5)], "sorted() works because __lt__ exists."
    assert max(Version(1), Version(1, 1)) == Version(1, 1), "max works too."


def test_version_equality_and_str():
    assert Version(1, 2) == Version(1, 2, 0), "A default field takes part in ==."
    assert str(Version(1, 2)) == "1.2.0", "__str__ writes major.minor.patch (you may add this method by hand)."
    assert repr(Version(1, 2)) == "Version(major=1, minor=2, patch=0)", "repr stays the generated one."


def test_version_is_frozen_and_hashable():
    v = Version(1, 2, 3)
    with pytest.raises(dataclasses.FrozenInstanceError):
        v.major = 9
    assert v == Version(1, 2, 3), "A rejected assignment changes nothing."
    assert {Version(1), Version(1, 0, 0)} == {Version(1)}, "frozen=True with eq=True gives __hash__: equal versions are one set element."
    assert {Version(1, 2): "a"}[Version(1, 2)] == "a", "Frozen dataclasses can be dict keys."


def test_playlist_is_not_frozen_and_not_hashable():
    p = Playlist("p")
    p.name = "q"
    assert p.name == "q", "Playlist stays mutable: do not freeze it."
    with pytest.raises(TypeError):
        hash(p)


def test_field_metadata():
    by_name = {f.name: f for f in dataclasses.fields(Playlist)}
    assert by_name["songs"].default_factory is list, "songs should use default_factory=list."
    assert by_name["plays"].compare is False and by_name["plays"].repr is False, "plays: repr=False and compare=False."
    params = dataclasses.fields(Version)
    assert [f.name for f in params] == ["major", "minor", "patch"], "Version fields in order: major, minor, patch."

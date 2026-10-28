import pytest

from solution import Sentence

W = ["the", "quick", "brown", "fox"]


def test_len_and_str():
    s = Sentence(W)
    assert len(s) == 4, "len(s) is the number of words. Define __len__."
    assert str(s) == "the quick brown fox", "str(s) joins the words with single spaces."


def test_int_index():
    s = Sentence(W)
    assert s[0] == "the" and s[1] == "quick", "s[i] returns the word."
    assert s[-1] == "fox", "Negative index counts from the end."
    with pytest.raises(IndexError):
        s[4]


def test_slice_returns_sentence():
    s = Sentence(W)
    part = s[1:3]
    assert isinstance(part, Sentence), "A slice must return a Sentence, not a list. Wrap the sliced list with type(self)(...)."
    assert list(part._words) == ["quick", "brown"], "s[1:3] holds 'quick' and 'brown'."
    assert str(part) == "quick brown", "str of the slice should be 'quick brown'."


def test_slice_forms():
    s = Sentence(W)
    assert str(s[:2]) == "the quick", "s[:2] takes the first two words."
    assert str(s[2:]) == "brown fox", "s[2:] takes from index 2."
    assert str(s[::2]) == "the brown", "A step works too."
    assert str(s[::-1]) == "fox brown quick the", "A negative step reverses."
    assert str(s[-2:]) == "brown fox", "Negative start works."


def test_slice_out_of_range_is_empty_not_error():
    s = Sentence(W)
    assert isinstance(s[10:20], Sentence) and len(s[10:20]) == 0, "Slices never raise IndexError; out of range gives an empty Sentence."
    assert str(s[10:20]) == "", "An empty Sentence prints as an empty string."


def test_slice_is_a_copy():
    s = Sentence(W)
    part = s[:2]
    part._words.append("x")
    assert len(s) == 4, "A slice must be independent of the original."


def test_bad_key_type():
    s = Sentence(W)
    with pytest.raises(TypeError):
        s["a"]
    with pytest.raises(TypeError):
        s[1.5]


def test_subclass_gets_own_type_back():
    class Shout(Sentence):
        pass

    part = Shout(W)[:2]
    assert type(part) is Shout, "Use type(self)(...) so a subclass slices into its own type."


def test_iteration_and_repr():
    s = Sentence(W)
    assert list(s) == W, "Iteration works through __getitem__ and __len__."
    assert repr(s[:2]) == "Sentence(['the', 'quick'])", "repr of a slice should be Sentence(['the', 'quick'])."

import pytest

from target import chunk


def test_exact_division():
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]], "Four items in pieces of 2 make two full pieces."


def test_last_piece_is_shorter():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]], "The leftover item must form a shorter last piece."


def test_size_bigger_than_list():
    assert chunk([1, 2], 5) == [[1, 2]], "A size larger than the list gives one short piece."


def test_empty_list_gives_no_pieces():
    assert chunk([], 3) == [], "An empty list has no pieces: the result is [], not [[]]."


def test_pieces_are_lists():
    assert chunk([1, 2, 3], 3) == [[1, 2, 3]], "Pieces must be lists, not tuples."
    assert type(chunk([1, 2], 1)[0]) is list, "Pieces must be lists."


def test_input_is_not_changed():
    data = [1, 2, 3, 4, 5]
    chunk(data, 2)
    assert data == [1, 2, 3, 4, 5], "chunk must not modify the list it was given."


def test_size_one():
    assert chunk([7, 8], 1) == [[7], [8]], "Size 1 puts every item in its own piece."


@pytest.mark.parametrize("bad", [0, -1, -5])
def test_bad_size_raises(bad):
    with pytest.raises(ValueError, match="positive"):
        chunk([1, 2, 3], bad)

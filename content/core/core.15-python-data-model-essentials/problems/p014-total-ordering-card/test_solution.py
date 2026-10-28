import pytest

from solution import Card


def test_validation():
    for bad in (("1", "hearts"), ("A", "stars"), (10, "hearts")):
        with pytest.raises(ValueError):
            Card(*bad)


def test_rank_order_not_string_order():
    assert Card("2", "clubs") < Card("10", "clubs"), "Rank 2 is lower than 10. Compare positions in RANKS, not strings."
    assert Card("10", "clubs") < Card("J", "clubs"), "10 is lower than J."
    assert Card("K", "clubs") < Card("A", "clubs"), "K is lower than A."


def test_suit_breaks_ties():
    assert Card("A", "clubs") < Card("A", "spades"), "Same rank: compare suits (clubs < diamonds < hearts < spades)."
    assert Card("5", "spades") < Card("6", "clubs"), "Rank beats suit: a 5 of spades is lower than a 6 of clubs."


def test_all_comparisons_exist():
    a, b = Card("10", "hearts"), Card("J", "clubs")
    assert a < b and a <= b, "< and <= should hold."
    assert b > a and b >= a, "> and >= should hold. Did you add @total_ordering?"
    assert not (a > b) and not (a >= b), "a is not greater than b."
    assert a <= Card("10", "hearts") and a >= Card("10", "hearts"), "<= and >= are True for equal cards."


def test_equality():
    assert Card("Q", "hearts") == Card("Q", "hearts"), "Same rank and suit means equal."
    assert Card("Q", "hearts") != Card("Q", "spades"), "Different suit means not equal."
    assert not (Card("Q", "hearts") == "Q of hearts"), "A Card is not equal to a string."


def test_sorted_and_max():
    cards = [Card("A", "clubs"), Card("2", "spades"), Card("10", "hearts"), Card("10", "clubs")]
    assert [repr(c) for c in sorted(cards)] == ["Card('2', 'spades')", "Card('10', 'clubs')", "Card('10', 'hearts')", "Card('A', 'clubs')"], "sorted() should order by rank, then suit."
    assert repr(max(cards)) == "Card('A', 'clubs')", "max() should find the highest card."


def test_hashable_and_consistent():
    assert hash(Card("A", "spades")) == hash(Card("A", "spades")), "Equal cards need equal hashes."
    assert len({Card("A", "spades"), Card("A", "spades"), Card("K", "spades")}) == 2, "A set should drop duplicate cards. Define __hash__."


def test_repr_and_foreign_lt():
    assert repr(Card("A", "spades")) == "Card('A', 'spades')", "repr should be Card('A', 'spades')."
    with pytest.raises(TypeError):
        Card("A", "spades") < 3

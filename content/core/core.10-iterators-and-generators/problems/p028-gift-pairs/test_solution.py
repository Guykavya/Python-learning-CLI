from solution import gift_pairs

ITEMS = [("pen", 20), ("book", 50), ("mug", 30), ("cap", 30), ("bag", 70)]


def test_basic():
    assert gift_pairs(ITEMS, 50) == [("pen", "mug"), ("pen", "cap")], "Every pair of two different items whose prices add up to the budget, earlier item first."


def test_not_same_item_twice():
    result = gift_pairs(ITEMS, 100)
    assert ("book", "book") not in result, "Never pair an item with itself: use combinations, not combinations_with_replacement or two full loops."
    assert result == [("mug", "bag"), ("cap", "bag")], "mug+bag and cap+bag cost 100."


def test_each_pair_once():
    result = gift_pairs([("a", 1), ("b", 2)], 3)
    assert result == [("a", "b")], "Each pair once, earlier item first. Did you use permutations?"


def test_none():
    assert gift_pairs(ITEMS, 5) == [], "No pair fits: empty list."


def test_one_or_zero_items():
    assert gift_pairs([("pen", 20)], 40) == [], "One item cannot make a pair."
    assert gift_pairs([], 10) == [], "No items, no pairs."


def test_same_price_two_items():
    assert gift_pairs([("x", 25), ("y", 25)], 50) == [("x", "y")], "Two DIFFERENT items with the same price are a valid pair."

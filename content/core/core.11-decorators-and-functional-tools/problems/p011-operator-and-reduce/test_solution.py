import pytest

from solution import largest, product, sort_by_price, sort_people


def test_sort_by_price():
    items = [("tea", 20), ("cake", 50), ("bun", 20)]
    assert sort_by_price(items) == [("tea", 20), ("bun", 20), ("cake", 50)], "Sort by index 1 (the price) with key=itemgetter(1). Equal prices keep their order."
    assert items == [("tea", 20), ("cake", 50), ("bun", 20)], "Do not sort the input in place. Use sorted(), which returns a new list."


def test_sort_by_price_not_by_name():
    items = [("apple", 90), ("zebra", 10)]
    assert sort_by_price(items) == [("zebra", 10), ("apple", 90)], "You sorted by name. The key must pick the price, at index 1."


def test_sort_people():
    people = [
        {"name": "Ann", "city": "Pune", "age": 30},
        {"name": "Bo", "city": "Agra", "age": 41},
        {"name": "Cy", "city": "Pune", "age": 25},
    ]
    names = [p["name"] for p in sort_people(people)]
    assert names == ["Bo", "Cy", "Ann"], "Sort by city first, then by age: key=itemgetter('city', 'age') gives a tuple key."
    assert [p["name"] for p in people] == ["Ann", "Bo", "Cy"], "Do not change the input list."


def test_product():
    assert product([2, 3, 4]) == 24, "reduce(mul, nums, 1) multiplies all the numbers."
    assert product([]) == 1, "The product of no numbers is 1. Give reduce a start value of 1, or it fails on an empty list."
    assert product([7]) == 7, "One number: the product is that number."
    assert product([5, 0, 3]) == 0, "Any zero makes the product 0."


def test_largest():
    assert largest([3, 9, 2]) == 9, "Keep the bigger of (best so far, next) at each step."
    assert largest([-5, -2, -9]) == -2, "Do not start from 0: for all-negative lists the answer is negative."
    assert largest([4]) == 4, "One item: that item is the largest."


def test_largest_empty():
    with pytest.raises(ValueError):
        largest([])

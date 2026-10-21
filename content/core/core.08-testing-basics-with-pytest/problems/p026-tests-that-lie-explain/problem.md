# Explain: tests that cannot fail

This is the assessed explanation for the module. A student shows you this test file and says "all
green, so my code is correct":

```python
from shop import apply_discount, total, add_to_cart

cart = []


def test_total():
    prices = [10, 20, 30]
    assert total(prices) == total(prices)


def test_discount():
    result = apply_discount(100, 10)
    print(result)


def test_add_one():
    add_to_cart(cart, "pen")
    assert len(cart) == 1


def test_add_two():
    add_to_cart(cart, "ink")
    assert len(cart) == 2


def test_everything():
    assert total([1, 2]) == 3
    assert apply_discount(50, 10) == 45
    assert apply_discount(50, 0) == 50
    assert total([]) == 0
    assert total([5]) == 5
    assert apply_discount(100, 100) == 0
```

In `answer.md`:

1. For `test_total` and `test_discount`, say why each one can **never fail**, and what a test is
   supposed to do instead. Rewrite both so that they can fail.
2. `test_add_two` passes today. Explain why it is fragile (**order**, **shared state**), what
   happens if you run only that test, and how to fix it.
3. `test_everything` has six asserts in one test. Name two problems this causes and say how you
   would restructure it.
4. Give a one-line check ("if I break the code on purpose, does ...?") that tells you whether a
   test is worth keeping, and use it on `test_total`.
5. "All green, so my code is correct." Give two reasons why this is not true even for a good test
   suite.

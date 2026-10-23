**1. Two tests that can never fail.**
`test_total` compares `total(prices)` with `total(prices)`: the same call twice gives the same
value, so the assert is always true, whatever `total` does (even if it returns `None`).
`test_discount` has no `assert` at all: it only prints the result, and pytest does not read
printed text, so the test passes unless the function crashes. A test must compare the result with
an **expected value chosen independently**, worked out by hand before running the code.

```python
def test_total():
    assert total([10, 20, 30]) == 60, "10 + 20 + 30 is 60."

def test_discount():
    assert apply_discount(100, 10) == 90, "10 percent off 100 is 90."
```

**2. Order and shared state.** `cart` is one list shared by all tests. `test_add_two` expects the
cart to already contain "pen", which only `test_add_one` put there. It passes only if
`test_add_one` ran before it, in the same run. Run alone (`pytest -k add_two`), the cart has one
item and `len(cart) == 2` fails. Tests must be **independent**: any one, in any order, alone. Fix:
create the cart inside each test: `cart = []` first, then `add_to_cart(cart, "ink")` and
`assert cart == ["ink"]`, or add both items inside the test that needs two.

**3. Six asserts in one test.** (a) The first failing assert stops the test, so the later five
never run and you do not know whether they would pass. (b) The test name `test_everything` does
not say which case broke, and the failure report points to one line among six. Restructure into
small named tests (`test_total_of_empty_list_is_zero`, `test_discount_zero_percent`, ...) or one
`parametrize` table of `(arguments, expected)` rows, where every row is reported separately.

**4. The "break it on purpose" check.** Change the code so it is wrong (return 0 from `total`).
Does the test turn red? If not, it is not testing anything. `test_total` stays green even if
`total` returns `None`, so it should be deleted or rewritten.

**5. Why "all green" does not mean "correct".** (a) A suite only covers the cases someone thought
of; inputs nobody tried can still be wrong, and edge cases may be missing. (b) The tests themselves
can be wrong: an expected value that was copied from the code's output, or a test that passes for
the wrong reason (like the two above). Green means "no known case failed", and it is only as good
as the tests.

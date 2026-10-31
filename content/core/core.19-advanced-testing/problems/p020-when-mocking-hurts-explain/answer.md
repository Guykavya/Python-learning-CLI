**1. Why it passes.** The mock repository returns 10 for any item and the mock tax returns 11 for
any input. So `result == 11` is true whatever `checkout` computes in between: it would be true for
`tax.apply(0)` too. The assertion only proves that the return value of `tax.apply` is passed back.
`price_of.assert_called_once_with("pen")` proves that one lookup happened, which the broken version
also does for a one-item cart. Coverage says 100% because every line ran, but running a line is not
checking its result.

**2. The kind of mistake.** The test checks the **wiring** (who calls whom), not the **behaviour**
(which number comes out). It is tied to the implementation, and the mocks lie: they return answers
that do not depend on the input, so the logic between them is never tested. Nobody tests the
multiplication by quantity, the sum over several items, or an empty cart.

**3. A better test.** Use a fake repository and a simple tax with hand-computed numbers:

```python
class FakeRepo:
    def __init__(self, prices): self.prices = prices
    def price_of(self, item): return self.prices[item]

class TenPercent:
    def apply(self, amount): return amount * 1.1

def test_checkout_adds_up_items_and_quantities():
    repo = FakeRepo({"pen": 10, "book": 25})
    cart = [("pen", 3), ("book", 2)]          # 30 + 50 = 80
    assert checkout(repo, TenPercent(), cart) == pytest.approx(88)
```

The broken version returns 11 (10 * 1.1) and fails. Add a test for an empty cart (0). The expected
value comes from arithmetic done by hand, not from the code.

**4. When mocks are right.** Use a mock or spy when the **call itself is the result**: sending an
email, charging a card, writing to a log. There is no return value to check, so "was it called once
with these arguments?" is the behaviour. Also use one for something slow or dangerous that has no
simple fake (a payment gateway), and to force rare errors (`side_effect=TimeoutError`). Rule of
thumb: fake or use real objects for **data and logic**, mock only the **edges where the outside world
is touched**, and always assert on results before you assert on calls.

# Explain: the test that cannot fail

A team has this function and this test. The test is green and coverage shows 100%.

```python
def checkout(repo, tax, cart):
    """cart is a list of (item, quantity). Return the final price with tax."""
    subtotal = 0
    for item, quantity in cart:
        subtotal += repo.price_of(item) * quantity
    return tax.apply(subtotal)
```

```python
from unittest.mock import Mock

def test_checkout():
    repo = Mock()
    repo.price_of.return_value = 10
    tax = Mock()
    tax.apply.return_value = 11

    result = checkout(repo, tax, [("pen", 1)])

    repo.price_of.assert_called_once_with("pen")
    tax.apply.assert_called_once()
    assert result == 11
```

Next month someone "simplifies" `checkout` to this broken version, and the test **still passes**:

```python
def checkout(repo, tax, cart):
    subtotal = repo.price_of(cart[0][0])        # ignores quantity and every other item
    return tax.apply(subtotal)
```

In `answer.md` (about 300 to 450 words), explain:

1. **Why it passes.** Which parts of the test are real checks and which are decoration? What does
   `assert result == 11` actually prove?
2. **What kind of mistake the test makes.** Name it (for example "testing the wiring / the
   implementation") and say which behaviour of `checkout` nobody tests.
3. **A better test.** Describe (with a few lines of code) a test with a fake repository (a dict) and a
   simple real or fake tax, whose expected value you worked out by hand, that fails on the broken
   version.
4. **When mocks are the right tool.** Give two situations where a mock or spy is the best choice, and a
   one-sentence rule of thumb for what to mock.

**Example** of the level of detail expected for one part:

> 1. The mock returns 10 for any item and the tax mock returns 11 for any input, so the result is
> 11 whatever `checkout` computes in between. The test would pass if `checkout` returned
> `tax.apply(0)`.

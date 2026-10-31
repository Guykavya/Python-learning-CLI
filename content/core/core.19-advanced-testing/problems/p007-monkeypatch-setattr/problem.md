# Write tests: monkeypatch.setattr

`monkeypatch.setattr(obj, "name", value)` swaps an attribute for the length of **one test** and
puts the original back afterwards, even when the test fails. Use it to change a constant or to
replace a helper that is slow or dangerous.

The code under test calls a helper that needs a network, so without patching it, `checkout` just
raises:

```python
TAX_RATE = 0.2


def fetch_discount(code):
    """Ask the discount server how much the code is worth (slow, needs the network)."""
    raise RuntimeError("no network in tests: patch fetch_discount")


def price_with_tax(net):
    return round(net * (1 + TAX_RATE), 2)


def checkout(net, code):
    """Take the discount off, then add tax. The price never goes below zero."""
    discount = fetch_discount(code)
    return price_with_tax(max(net - discount, 0))
```

In `solution.py` write `import target` (so you patch the module that the functions read from)
and tests that

- **pass** on the code above (so you must replace `fetch_discount` wherever you call `checkout`),
- **fail** on each of six buggy versions the checker tries (it names the survivor),
- take `monkeypatch` as a parameter in **at least four** tests, and
- contain at least five test functions.

Save the code above as `target.py` next to your `solution.py` and run
`python -m pytest solution.py` to try your tests. Give every `assert` a message.

**Example of one test**

```python
import target


def test_tax_rate_is_used(monkeypatch):
    monkeypatch.setattr(target, "TAX_RATE", 0.5)
    assert target.price_with_tax(10) == 15.0, "price_with_tax must read TAX_RATE, not a fixed number."
```

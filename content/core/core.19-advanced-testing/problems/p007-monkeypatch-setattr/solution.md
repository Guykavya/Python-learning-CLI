## Approach

Replace the slow helper with a tiny **stub** (`lambda code: 4`) so the test controls the
discount, and patch `TAX_RATE` so a hard-coded rate cannot hide. Patch on the **module**
(`import target`), because `checkout` looks the names up in the module's globals at call time.

## Code

```python
import target


def test_price_with_tax_reads_the_rate(monkeypatch):
    monkeypatch.setattr(target, "TAX_RATE", 0.5)
    assert target.price_with_tax(10) == 15.0


def test_price_is_rounded_to_cents():
    assert target.price_with_tax(10.55) == 12.66


def test_discount_comes_off_before_tax(monkeypatch):
    monkeypatch.setattr(target, "fetch_discount", lambda code: 4)
    monkeypatch.setattr(target, "TAX_RATE", 0.25)
    assert target.checkout(20, "SAVE4") == 20.0


def test_discount_larger_than_price(monkeypatch):
    monkeypatch.setattr(target, "fetch_discount", lambda code: 50)
    assert target.checkout(10, "HUGE") == 0.0


def test_checkout_sends_the_code_on(monkeypatch):
    seen = []
    monkeypatch.setattr(target, "fetch_discount", lambda code: seen.append(code) or 0)
    target.checkout(10, "SPRING")
    assert seen == ["SPRING"]
```

## Cost

A patch costs one dictionary assignment and is undone at the end of the test automatically.

## Another way

Better design: pass the discount function in as a parameter (`checkout(net, code, lookup)`), then
no patching is needed (chapter section 7: dependency injection is the best seam).

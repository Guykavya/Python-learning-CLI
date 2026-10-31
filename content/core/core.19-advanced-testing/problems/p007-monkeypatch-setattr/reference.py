import target


def test_price_with_tax_reads_the_rate(monkeypatch):
    monkeypatch.setattr(target, "TAX_RATE", 0.5)
    assert target.price_with_tax(10) == 15.0, "price_with_tax must use TAX_RATE, not a fixed number."


def test_price_is_rounded_to_cents():
    assert target.price_with_tax(10.55) == 12.66, "Round to two decimals (cents), not fewer."


def test_discount_comes_off_before_tax(monkeypatch):
    monkeypatch.setattr(target, "fetch_discount", lambda code: 4)
    monkeypatch.setattr(target, "TAX_RATE", 0.25)
    assert target.checkout(20, "SAVE4") == 20.0, "(20 - 4) * 1.25 = 20.0: discount first, then tax."


def test_discount_larger_than_price_gives_zero(monkeypatch):
    monkeypatch.setattr(target, "fetch_discount", lambda code: 50)
    assert target.checkout(10, "HUGE") == 0.0, "The price never goes below zero."


def test_checkout_sends_the_code_on(monkeypatch):
    seen = []

    def fake(code):
        seen.append(code)
        return 0

    monkeypatch.setattr(target, "fetch_discount", fake)
    target.checkout(10, "SPRING")
    assert seen == ["SPRING"], "fetch_discount must be called once with the customer's code."


def test_no_discount_only_tax(monkeypatch):
    monkeypatch.setattr(target, "fetch_discount", lambda code: 0)
    assert target.checkout(10, "X") == 12.0, "With a discount of 0 only the 20% tax is added."

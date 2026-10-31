## Hint 1

What lines would every test repeat? Creating a `Cart()` and adding the apples and the bread.
Put exactly those lines into a function and mark it `@pytest.fixture`. What must it `return`?

## Hint 2

Which behaviours does `Cart` have? Total, count, adding a **second** time, removing, removing
something that is not there, a bad quantity. One test each. A buggy `Cart` always breaks one of
those, so a missing test lets that bug live.

```
@pytest.fixture
def cart():
    c = Cart(); c.add(apple...); c.add(bread...); return c

def test_total(cart):  assert cart.total() == 6.0
def test_count(cart):  ...
with pytest.raises(KeyError): cart.remove("milk")
```

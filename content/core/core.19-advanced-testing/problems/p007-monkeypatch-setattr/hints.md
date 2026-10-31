## Hint 1

`checkout` calls `fetch_discount`, which raises unless replaced. Which module object must you
patch, and what name inside it? `monkeypatch.setattr(target, "fetch_discount", ...)` replaces
it with what? (A function that takes `code` and returns a number.)

## Hint 2

Each bug is one wrong line, so give each line its own test. Patch `TAX_RATE` to a value other
than 0.2 to expose a hard-coded rate. Use a discount **bigger** than the price. Record the code
that your fake receives. And one test without any patching for rounding.

```
monkeypatch.setattr(target, "TAX_RATE", 0.25)
monkeypatch.setattr(target, "fetch_discount", lambda code: 4)
assert target.checkout(20, "X") == 20.0
seen = []; fake appends code; assert seen == ["SPRING"]
```

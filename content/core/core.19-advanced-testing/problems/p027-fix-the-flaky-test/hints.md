## Hint 1

For each test ask: what does its result depend on **besides the code under test**? Name it (the clock,
the random generator, the order of a set, data left by another test). Which tests of the file have such a
hidden input?

## Hint 2

Give every hidden input to the test instead of letting it come from outside: `monkeypatch.setattr` for
the hour (many hours, with parametrize), a seeded `random.Random` for the dice, `sorted(...)` or `set(...)`
for an order that is not specified, and an `autouse` fixture that calls `target.clear()` before and after
each test.

## Hint 3

```
fixture (autouse): target.clear(); yield; target.clear()
greeting: parametrize (hour, text) over 0, 11, 12, 17, 18, 23; monkeypatch.setattr(target, "current_hour", lambda: hour)
unique_tags: sorted(unique_tags([...])) == [...]
roll_dice: rolls = roll_dice(600, random.Random(1)); length 600, set(rolls) == {1..6}; and compare with Random(5)
records: each test starts from an empty store; the "next record number" test records its own events first
```

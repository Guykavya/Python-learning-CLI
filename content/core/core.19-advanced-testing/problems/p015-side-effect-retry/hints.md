## Hint 1

Which sequences of results can the client produce? Name them: ok; fail then ok; fail, fail, ok;
fail, fail, fail; a different error. Which line of the function does each one exercise?

## Hint 2

Give every failure a different message (`"one"`, `"two"`, `"three"`) and use
`pytest.raises(ConnectionError, match="three")`. Then you can see **which** error came out. Also look
at `client.get.call_count`: it counts the calls, so it exposes both too few and too many.

## Hint 3

```
client = Mock(); client.get.side_effect = [ ... items ... ]
success first time:        side_effect = ["page"]            -> call_count == 1
success on last attempt:   [CE("1"), CE("2"), "page"]        -> "page", call_count == 3
all fail:                  [CE("1"), CE("2"), CE("3")]       -> raises match "3", call_count == 3
other error:               [ValueError("bad")]               -> raises ValueError, call_count == 1
attempts=1 and attempts=5: call_count == attempts when all fail (use side_effect=ConnectionError("x"))
attempts=0:                raises ValueError
```

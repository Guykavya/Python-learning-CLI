# Mock basics: test `notify`

`notify` sends a message through a `sender` object (an email client, an SMS gateway, ...). In a unit
test you do not want to send anything, so you hand it a `Mock` and then ask the mock what it was
told. The code under test:

```python
def notify(sender, user, message):
    """Send message to the user through sender. Return True if sent, False if the message is blank."""
    text = message.strip()
    if not text:
        return False
    sender.send(user["email"], "[notice] " + text)
    return True
```

In `solution.py` write tests (`from target import notify`, `from unittest.mock import Mock`) that:

- build `sender = Mock()` and check with `sender.send.assert_called_once_with(address, text)` that
  the right address and the right text (with the prefix, with outer spaces removed) were sent;
- check the return value in both cases;
- check with `sender.send.assert_not_called()` that a blank message (`""` and `"   "`) sends nothing.

Write at least 4 test functions. The checker has seven buggy versions of `notify`.

**Example**

```python
def test_prefix_is_added():
    sender = Mock()
    notify(sender, {"name": "Ann", "email": "ann@example.com"}, "hi")
    sender.send.assert_called_once_with("ann@example.com", "[notice] hi")
```

**How this is checked.** Your `solution.py` is a file of pytest tests. The checker copies it next
to the code above (saved as `target.py`) and runs real pytest, first on the **correct** code (all
your tests must pass), then on several **buggy copies** (at least one of your tests must fail on
each; the report names any bug that survives). To try your tests yourself, save the code as
`target.py` in your folder and run `python -m pytest solution.py -p no:cacheprovider`.

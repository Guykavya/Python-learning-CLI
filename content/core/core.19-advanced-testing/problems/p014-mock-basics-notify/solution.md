## Approach

A mock is a test spy. `Mock()` accepts any call and remembers it, so `sender.send` exists without
you defining it. `assert_called_once_with(...)` checks both **how many times** and **with what
arguments**, which kills three bugs at once (wrong address, missing prefix, double send).
`assert_not_called()` proves that a blank message does not touch the sender. The return value is a
separate promise, so it gets its own asserts.

## Code

```python
from unittest.mock import Mock

from target import notify

USER = {"name": "Ann", "email": "ann@example.com"}


def test_sends_prefixed_text_to_the_email():
    sender = Mock()
    notify(sender, USER, "hi")
    sender.send.assert_called_once_with("ann@example.com", "[notice] hi")


def test_outer_spaces_are_removed():
    sender = Mock()
    notify(sender, USER, "  hi  ")
    sender.send.assert_called_once_with("ann@example.com", "[notice] hi")


def test_blank_message_sends_nothing():
    for blank in ("", "   "):
        sender = Mock()
        assert notify(sender, USER, blank) is False, "A blank message must return False."
        sender.send.assert_not_called()


def test_returns_true_when_sent():
    assert notify(Mock(), USER, "hi") is True, "A sent message must return True."
```

## Complexity

Not applicable.

## Another way

Check `sender.send.call_args` or `sender.send.call_count` by hand. `assert_called_once_with` is the
same check with a better failure message.

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

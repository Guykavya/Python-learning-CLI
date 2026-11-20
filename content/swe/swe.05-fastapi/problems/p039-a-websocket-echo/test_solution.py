import pytest
from fastapi.testclient import TestClient

from solution import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_messages_come_back_upper_cased(client):
    with client.websocket_connect("/ws/echo") as ws:
        for text in ("hello", "Mixed Case 42", "bye now"):
            ws.send_text(text)
            got = ws.receive_text()
            assert got == text.upper(), f"Sent {text!r}, expected {text.upper()!r} back, got {got!r}. Use text.upper()."


@pytest.mark.parametrize("word", ["bye", "BYE", "  Bye  "])
def test_bye_says_goodbye_and_closes_with_1000(client, word):
    with client.websocket_connect("/ws/echo") as ws:
        ws.send_text(word)
        got = ws.receive_text()
        assert got == "goodbye", (
            f"For {word!r} the server must answer 'goodbye', got {got!r}. Compare text.strip().lower() == 'bye'.")
        ws.send_text("are you still there?")          # a server that did not close would answer this
        message = ws.receive()
        assert message["type"] == "websocket.close", (
            f"After 'goodbye' the server must close the socket, but it answered {message!r}. "
            "Call await websocket.close(code=1000) and return from the endpoint.")
        assert message["code"] == 1000, f"Close with code 1000 (normal closure), got {message['code']}"


def test_the_client_can_leave_first(client):
    with client.websocket_connect("/ws/echo") as ws:
        ws.send_text("one")
        assert ws.receive_text() == "ONE"
    # leaving the "with" block disconnects; the endpoint must catch WebSocketDisconnect quietly
    with client.websocket_connect("/ws/echo") as ws:
        ws.send_text("two")
        assert ws.receive_text() == "TWO", "A new connection after a disconnect must work normally."

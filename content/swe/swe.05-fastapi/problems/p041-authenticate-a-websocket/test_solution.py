import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from solution import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_a_good_token_can_chat(client):
    with client.websocket_connect("/ws/chat?token=t-asha") as ws:
        ws.send_text("hi")
        assert ws.receive_text() == "asha: hi", "Answer with '<user>: <text>' where user comes from the token."
    with client.websocket_connect("/ws/chat?token=t-ben") as ws:
        ws.send_text("hello")
        assert ws.receive_text() == "ben: hello"


@pytest.mark.parametrize("url", ["/ws/chat?token=nope", "/ws/chat?token=", "/ws/chat", "/ws/chat?token=T-ASHA"])
def test_bad_tokens_are_refused_during_the_handshake(client, url):
    with pytest.raises(WebSocketDisconnect) as info:
        with client.websocket_connect(url) as ws:
            ws.send_text("let me in")
            ws.receive_text()
    assert info.value.code == 1008, (
        f"{url}: close with code 1008 (policy violation), got {info.value.code}.")


@pytest.mark.parametrize("url", ["/ws/chat?token=nope", "/ws/chat"])
def test_refusal_happens_before_accept(client, url):
    accepted = False
    try:
        with client.websocket_connect(url):
            accepted = True
    except WebSocketDisconnect:
        pass
    assert not accepted, (
        f"{url}: the handshake succeeded, so the server called accept() before checking the token. "
        "Check first; call websocket.close(code=1008) without accept().")


def test_exactly_the_limit_is_allowed(client):
    with client.websocket_connect("/ws/chat?token=t-ben") as ws:
        ws.send_text("x" * 4096)
        assert ws.receive_text() == "ben: " + "x" * 4096, "4096 bytes is the limit itself and must still be accepted (use >, not >=)."


def test_too_big_closes_with_1009(client):
    with client.websocket_connect("/ws/chat?token=t-ben") as ws:
        ws.send_text("x" * 4097)
        message = ws.receive()
        assert message["type"] == "websocket.close", (
            f"A 4097-byte message must close the connection, but the server answered {message!r}.")
        assert message["code"] == 1009, f"Use close code 1009 (message too big), got {message['code']}"


def test_the_limit_counts_bytes_not_characters(client):
    with client.websocket_connect("/ws/chat?token=t-asha") as ws:
        ws.send_text("é" * 2049)                        # 2049 characters, 4098 bytes in UTF-8
        message = ws.receive()
        assert message["type"] == "websocket.close" and message.get("code") == 1009, (
            "'é' * 2049 is only 2049 characters but 4098 bytes: measure len(text.encode('utf-8')), not len(text).")


def test_the_limit_applies_to_every_message(client):
    with client.websocket_connect("/ws/chat?token=t-asha") as ws:
        ws.send_text("small")
        assert ws.receive_text() == "asha: small"
        ws.send_text("y" * 5000)
        assert ws.receive()["type"] == "websocket.close", "The size check must run inside the loop, for every message."

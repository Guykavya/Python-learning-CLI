import asyncio
import json

import anyio
import pytest
from fastapi.testclient import TestClient

from solution import ConnectionManager, app, manager


# ---------- helpers ----------

def receive_json(ws, seconds=2.0):
    """ws.receive_json(), but fail with a clear message instead of waiting forever."""
    stream = getattr(ws, "_send_rx", None)          # the test session's message stream (Starlette 1.x)
    if stream is None:
        return ws.receive_json()

    async def _get():
        with anyio.fail_after(seconds):
            return await stream.receive()

    try:
        message = ws.portal.call(_get)
    except TimeoutError:
        raise AssertionError(f"No message arrived within {seconds} s: a broadcast is missing or went to the wrong room.") from None
    if message["type"] == "websocket.close":
        raise AssertionError(f"The server closed the socket (code {message.get('code')}) instead of sending a message.")
    return json.loads(message["text"])


class FakeSocket:
    def __init__(self, name, dead=False):
        self.name, self.dead = name, dead
        self.accepted, self.sent = False, []

    async def accept(self):
        self.accepted = True

    async def send_json(self, message):
        if self.dead:
            raise RuntimeError("connection lost")
        self.sent.append(message)


@pytest.fixture(autouse=True)
def empty_manager():
    manager.rooms.clear()
    yield
    manager.rooms.clear()


# ---------- the class alone ----------

def test_connect_accepts_and_registers():
    m = ConnectionManager()
    a = FakeSocket("a")
    asyncio.run(m.connect("r1", a))
    assert a.accepted, "connect() must call await websocket.accept() first."
    assert m.count("r1") == 1 and m.rooms["r1"] == [a], f"connect() must add the socket to rooms['r1'], rooms is {m.rooms!r}"


def test_broadcast_reaches_only_its_room():
    m = ConnectionManager()
    a, b, c = FakeSocket("a"), FakeSocket("b"), FakeSocket("c")

    async def scenario():
        await m.connect("r1", a)
        await m.connect("r1", b)
        await m.connect("r2", c)
        await m.broadcast("r1", {"n": 1})

    asyncio.run(scenario())
    assert a.sent == [{"n": 1}] and b.sent == [{"n": 1}], "Every socket in the room must receive the message once."
    assert c.sent == [], "A socket in another room must receive nothing."


def test_dead_sockets_are_dropped_and_the_rest_still_receive():
    m = ConnectionManager()
    dead, b, c = FakeSocket("dead", dead=True), FakeSocket("b"), FakeSocket("c")

    async def scenario():
        for s in (dead, b, c):
            await m.connect("r1", s)
        await m.broadcast("r1", {"n": 1})

    asyncio.run(scenario())
    assert b.sent == [{"n": 1}], (
        "The socket right after a dead one got nothing. You removed the dead socket from the list while looping "
        "over that same list: loop over a copy, for connection in list(...).")
    assert c.sent == [{"n": 1}], "One dead socket must not stop the broadcast: catch the exception and carry on."
    assert m.count("r1") == 2 and dead not in m.rooms["r1"], "A socket whose send_json raised must be disconnected."


def test_empty_rooms_are_deleted_and_unknown_rooms_are_not_created():
    m = ConnectionManager()
    a = FakeSocket("a")
    asyncio.run(m.connect("r1", a))
    m.disconnect("r1", a)
    assert "r1" not in m.rooms, f"When the last socket leaves, delete the room (rooms is {m.rooms!r})."
    asyncio.run(m.broadcast("ghost", {"n": 1}))
    assert m.count("ghost") == 0
    assert "ghost" not in m.rooms, (
        "broadcast() or count() created an empty room 'ghost'. With a defaultdict, self.rooms[room] creates "
        "the key; use self.rooms.get(room, []).")


# ---------- the endpoints ----------

def test_three_sockets_in_two_rooms():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/rooms/team-7?user=asha") as asha:
            assert receive_json(asha) == {"event": "joined", "user": "asha"}, "The newcomer hears their own 'joined' event."
            with client.websocket_connect("/ws/rooms/team-7?user=ben") as ben:
                assert receive_json(asha) == {"event": "joined", "user": "ben"}, "Asha must hear that Ben joined."
                assert receive_json(ben) == {"event": "joined", "user": "ben"}
                with client.websocket_connect("/ws/rooms/team-9?user=dina") as dina:
                    assert receive_json(dina) == {"event": "joined", "user": "dina"}
                    ben.send_json({"task": 5})
                    expected = {"event": "message", "user": "ben", "data": {"task": 5}}
                    assert receive_json(asha) == expected, "A message must reach everyone in the room."
                    assert receive_json(ben) == expected, "The sender is in the room too, so he hears it."
                    dina.send_json({"hello": "nine"})
                    got = receive_json(dina)
                    assert got == {"event": "message", "user": "dina", "data": {"hello": "nine"}}, (
                        f"Dina received {got!r} before her own message: something from team-7 leaked into team-9.")
            assert receive_json(asha) == {"event": "left", "user": "ben"}, (
                "When Ben's socket closes, catch WebSocketDisconnect, disconnect him, and broadcast 'left' to the room.")
    assert manager.rooms == {}, f"After everyone left, manager.rooms must be empty, got {manager.rooms!r}"


def test_announce_from_http():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/rooms/team-7?user=asha") as asha, \
                client.websocket_connect("/ws/rooms/team-7?user=ben") as ben:
            receive_json(asha), receive_json(asha), receive_json(ben)       # the joined events
            r = client.post("/rooms/team-7/announce", params={"text": "standup"})
            assert r.json() == {"delivered_to": 2}, f"Two sockets are in team-7, got {r.json()}"
            for ws in (asha, ben):
                assert receive_json(ws) == {"event": "announcement", "text": "standup"}
        r = client.post("/rooms/empty/announce", params={"text": "anyone?"})
        assert r.json() == {"delivered_to": 0}, "An unknown room delivers to nobody."
        assert "empty" not in manager.rooms, "Announcing to an unknown room must not create it."

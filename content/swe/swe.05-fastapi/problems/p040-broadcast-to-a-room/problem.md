# Broadcast to a room

Chapter section 15.3 (and 15.2 for the basics). Build a small real-time chat: everyone connected to the same **room** hears what anyone in that room says; people in other rooms hear nothing.

## Part 1: `ConnectionManager`

A class that keeps the live connections per room, in `self.rooms` (a dict: room name → list of sockets).

| Method | What it does |
|---|---|
| `async connect(room, websocket)` | `await websocket.accept()`, then add the socket to the room |
| `disconnect(room, websocket)` | remove the socket; if the room is now empty, **delete the room** from `self.rooms` (no leak of empty rooms) |
| `async broadcast(room, message)` | `await socket.send_json(message)` for every socket of that room. If sending to one socket raises **any** exception, that socket is dead: `disconnect` it and **carry on** with the others. An unknown room is fine: nobody receives anything and **no empty room is created**. |
| `count(room)` | how many sockets the room has (0 for an unknown room, again without creating it) |

Careful: `broadcast` may remove sockets from the list **while it loops over it**. Loop over a copy (`list(...)`).

Make one module-level instance: `manager = ConnectionManager()`. The tests also check the class alone with fake sockets (objects with `async accept()` and `async send_json(message)`).

## Part 2: the endpoints

- **WebSocket `/ws/rooms/{room}?user=NAME`**: connect through `manager`; broadcast `{"event": "joined", "user": NAME}` to the room (the newcomer hears it too). Then, for every JSON message the client sends, broadcast `{"event": "message", "user": NAME, "data": <the message>}`. When the client leaves (`WebSocketDisconnect`): `disconnect`, then broadcast `{"event": "left", "user": NAME}` to those still in the room.
- **`POST /rooms/{room}/announce?text=...`**: an ordinary HTTP endpoint that broadcasts `{"event": "announcement", "text": TEXT}` and returns `{"delivered_to": <count of sockets in the room>}`.

## Example

```text
asha joins team-7       asha hears: joined asha
ben joins team-7        asha hears: joined ben     ben hears: joined ben
dina joins team-9       dina hears: joined dina
ben sends {"task": 5}   asha and ben hear: message ben {"task": 5}       dina hears nothing
POST /rooms/team-7/announce?text=standup  -> {"delivered_to": 2}; asha and ben hear it
ben leaves              asha hears: left ben
everyone leaves         manager.rooms == {}
```

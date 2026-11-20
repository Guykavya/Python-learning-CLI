## Hint 1

Start with the class and its tests (they need no server). What should `self.rooms` look like after two sockets join `"r1"`? Which dictionary method gives "the list for this room, or an empty list" **without** storing anything? Which one gives "the list, created if missing" for `connect`?

## Hint 2

- `connect`: `await websocket.accept()`, then `self.rooms.setdefault(room, []).append(websocket)`.
- `disconnect`: remove from the list, and `pop` the room when the list is empty.
- `broadcast`: `for connection in list(self.rooms.get(room, [])):` with `try: await connection.send_json(message)` / `except Exception: self.disconnect(room, connection)`. Why the `list(...)` copy? Removing item 0 of a list while a `for` is at index 0 makes the loop skip the next item.
- `count`: `len(self.rooms.get(room, []))`.

## Hint 3

```text
endpoint room_socket(websocket, room, user):
    await manager.connect(room, websocket)
    await manager.broadcast(room, {"event": "joined", "user": user})
    try:
        loop: data = await websocket.receive_json()
              await manager.broadcast(room, {"event": "message", "user": user, "data": data})
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
        await manager.broadcast(room, {"event": "left", "user": user})

announce(room, text): await broadcast(...); return {"delivered_to": manager.count(room)}
```

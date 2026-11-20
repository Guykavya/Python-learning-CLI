## Approach

The manager is a dict of lists plus three careful details: never create rooms by reading, delete rooms when they empty, and survive dead sockets while looping.

```python
class ConnectionManager:
    def __init__(self):
        self.rooms = {}                      # room name -> list of WebSocket

    async def connect(self, room, websocket):
        await websocket.accept()
        self.rooms.setdefault(room, []).append(websocket)

    def disconnect(self, room, websocket):
        sockets = self.rooms.get(room, [])
        if websocket in sockets:
            sockets.remove(websocket)
        if not sockets:
            self.rooms.pop(room, None)       # do not leak empty rooms

    async def broadcast(self, room, message):
        for connection in list(self.rooms.get(room, [])):     # a copy: disconnect() may change the list
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(room, connection)              # dead socket: drop it, keep going

    def count(self, room):
        return len(self.rooms.get(room, []))                   # .get: never creates a room
```

The endpoints are the chapter's (section 15.3): connect, announce the join, relay every JSON message, and on `WebSocketDisconnect` remove the socket **before** broadcasting `left` (otherwise the server would try to send to the socket that just closed).

Example of the copy trap: the room is `[dead, b, c]`. Without `list(...)`, the loop is at index 0 (`dead`), sending fails, `dead` is removed, the list becomes `[b, c]`, and the loop moves on to index 1, which is now `c`. `b` never gets the message. With the copy, the loop walks the old three-item list and the removal changes only the real one.

Why the tests check that no empty rooms appear: a busy server sees thousands of room names (one per team, per document...). A `defaultdict` read like `self.rooms[room]` in `broadcast` creates an entry for every room anybody ever announced to, and the dict grows forever.

## Complexity

`broadcast` is O(k) sends for a room of k sockets; `connect` is O(1); `disconnect` is O(k) (list removal). Memory is one list entry per open connection.

## Another way

Use a `set` per room instead of a list (`self.rooms.setdefault(room, set()).add(ws)`, `discard` to remove): removal is O(1) and duplicates are impossible. Send to all sockets **concurrently** with `asyncio.gather(*(send(ws) for ws in ...), return_exceptions=True)` so one slow client does not delay the others. And remember the limit of section 15.4: this manager lives in one process; several workers need a shared broker such as Redis pub/sub.

# Explain: does it block the event loop?

Each snippet below sits inside an `async def` handler of a busy async server. The event loop
serves hundreds of other requests from the same thread.

For **each** snippet, say:

1. **Blocks** the event loop or **does not block** (and roughly for how long, if that matters).
2. **Why**, in one sentence.
3. If it blocks: the **fix** (`await asyncio.to_thread(...)`, `loop.run_in_executor` with a
   process pool, or an async library), written as the line you would use.

```python
# 1
time.sleep(2)

# 2
response = requests.get("https://api.example.com/users")

# 3
await asyncio.sleep(2)

# 4
total = 0
for i in range(50_000_000):
    total += i * i

# 5
with open("config.toml") as f:          # a 2 KB file on a local SSD
    text = f.read()

# 6
response = await client.get("https://api.example.com/users")   # client is an httpx.AsyncClient

# 7
big = sum(range(10**8))

# 8
rows = db.execute("SELECT * FROM orders WHERE user_id = ?", (uid,)).fetchall()   # sqlite3
```

Write `answer.md`: one short paragraph or bullet per snippet (about 250 to 400 words in
total).

**Example of the level of detail expected (a different snippet)**

> *`data = json.loads(body)` on a 300-byte body.* **Blocks, but only for microseconds**, so it
> is fine: every line of Python "blocks" while it runs. What matters is how long. Parsing a
> 300-byte string takes far less than a millisecond. If `body` were a 200 MB file, parsing
> would freeze the loop for seconds, and it should go to `await asyncio.to_thread(json.loads,
> body)` (or better, a process pool, since parsing is CPU work).

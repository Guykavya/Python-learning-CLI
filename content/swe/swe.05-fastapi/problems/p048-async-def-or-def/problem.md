# `async def` or `def`?

Chapter sections 10.1 to 10.3 (and 11 for async databases). The keyword in front of an endpoint decides **where it runs**: `async def` runs on the event loop thread itself; plain `def` runs in a worker thread from a pool. The rule from section 10.1: *use `async def` only if everything slow inside it is awaited; if anything blocks, use plain `def`.*

Here are five endpoint bodies, written without the keyword. For **each** one, in `answer.md`, say whether you would write `async def` or `def`, and explain **why** in two to four sentences: what is slow in it (if anything), whether that slow part blocks or is awaited, and what would happen to *other* requests with the wrong choice.

```python
# 1. Pure computation, a few microseconds
@app.get("/area")
____ area(width: float, height: float):
    return {"area": width * height}

# 2. Calls another service with the requests library (blocking HTTP client)
@app.get("/weather/{city}")
____ weather(city: str):
    r = requests.get(f"https://weather.example/api/{city}", timeout=5)
    return r.json()

# 3. Calls another service with httpx's async client
@app.get("/weather2/{city}")
____ weather2(city: str, client: Annotated[httpx.AsyncClient, Depends(get_http_client)]):
    r = await client.get(f"https://weather.example/api/{city}", timeout=5)
    return r.json()

# 4. Uses a normal (synchronous) SQLAlchemy session
@app.get("/tasks/{task_id}")
____ get_task(task_id: int, session: Annotated[Session, Depends(get_session)]):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(404, "Task not found")
    return TaskOut.model_validate(task)

# 5. Reads a report file from disk
@app.get("/reports/{name}")
____ report(name: str):
    path = REPORTS_DIR / f"{name}.txt"
    return {"text": path.read_text(encoding="utf-8")}
```

Then answer one more question: endpoint 2 must stay `async def` because it also awaits something else. How can it call `requests.get` without freezing the event loop?

A good answer uses the words *event loop*, *blocking*, *await*, *thread pool* (or *worker thread*).

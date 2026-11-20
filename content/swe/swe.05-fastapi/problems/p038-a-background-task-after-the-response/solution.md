## Approach

```python
def send_welcome(outbox, email):
    try:
        outbox.send(to=email, subject="Welcome to TaskFlow", body=f"Hi {email}, thanks for signing up.")
    except Exception:
        # The response is already gone: the log is the only place a failure can be seen.
        logger.exception("welcome email to %s failed", email)


@app.post("/signup", status_code=201)
def signup(data: SignupIn, outbox: Annotated[Outbox, Depends(get_outbox)], background: BackgroundTasks):
    background.add_task(send_welcome, outbox, data.email)      # runs after the response is sent
    return {"email": data.email, "welcome": "queued"}
```

Example: `POST /signup {"email": "asha@example.com"}`. FastAPI sees the `BackgroundTasks` parameter and passes a fresh, empty task list. `add_task` stores `(send_welcome, (fake_outbox, "asha@example.com"))`. The endpoint returns; FastAPI sends the 201; only then does Starlette run the stored call, and the fake outbox gets its message.

Why the outbox is a **dependency** and not a global used directly inside `send_welcome`: the test swaps it with `app.dependency_overrides[get_outbox]`, so no real email is ever sent in a test and a failure can be simulated. The endpoint passes the outbox it received to the task, so the task uses the same (possibly fake) object.

Why catch everything in the task: there is nobody to report the error to. Without the `try`, the exception would end up in the server's error output with no context, and in some servers it can even break the connection. `logger.exception` records the email and the traceback.

## Complexity

O(1) work in the request; the email cost moves after the response. The client's wait no longer includes the mail server.

## Another way

For mail that **must** arrive, use a job queue (Celery, RQ, arq; section 14): the endpoint stores a job, a separate worker process sends it, retries on failure, and nothing is lost when the web server restarts. `BackgroundTasks` is fine for "nice to have" work such as a welcome email or an audit line.

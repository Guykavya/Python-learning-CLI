## Hint 1

How does an endpoint get hold of the background task list? The same way it gets anything else in FastAPI: by declaring a **parameter** with the right type. What type does section 14 use, and which method schedules a function with its arguments?

## Hint 2

`add_task(func, *args)` takes the function **itself** (no parentheses) and then its arguments. `background.add_task(send_welcome(outbox, email))` would call it right away and schedule its return value `None`. Inside `send_welcome`, wrap the `send` in `try` / `except Exception:` and call `logger.exception(...)` inside the `except`: it logs the message and the traceback.

## Hint 3

```text
def send_welcome(outbox, email):
    try: outbox.send(to=email, subject="Welcome to TaskFlow", body=f"Hi {email}, thanks for signing up.")
    except Exception: logger.exception("welcome email to %s failed", email)

def signup(data, outbox (Depends(get_outbox)), background: BackgroundTasks):
    background.add_task(send_welcome, outbox, data.email)
    return {"email": data.email, "welcome": "queued"}
```

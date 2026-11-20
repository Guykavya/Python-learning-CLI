# A background task after the response

Chapter sections 14 and 9.6. A new user signs up. Saving the user is quick, but sending the welcome email means talking to a mail server, which can take seconds or fail. The user should not wait for it, and a broken mail server must not turn a successful signup into an error.

`solution.py` already has:

- `Outbox`: the "mail server" (here it only keeps a list) with a method `send(to, subject, body)`.
- `get_outbox()`: a dependency that returns the app's outbox. The tests replace it with a **fake outbox** through `app.dependency_overrides[get_outbox]` (section 9.6), so they can see what was sent, or make sending fail.
- `POST /signup`: takes the JSON body `{"email": "..."}` and answers **201** `{"email": ..., "welcome": "queued"}`.

Your job:

1. Write `send_welcome(outbox, email)`. It calls `outbox.send(to=email, subject="Welcome to TaskFlow", body=f"Hi {email}, thanks for signing up.")`. If sending raises **any** exception, it must **not** crash: catch it and log it with `logger.exception("welcome email to %s failed", email)` (the given `logger`). The client already has its answer, so the log is the only place where a failure can be seen.
2. In `POST /signup`, add a `background: BackgroundTasks` parameter and schedule the email with `background.add_task(send_welcome, outbox, email)`. Do **not** call `send_welcome` directly in the endpoint.

## Example

```text
POST /signup {"email": "asha@example.com"}
  -> 201 {"email": "asha@example.com", "welcome": "queued"}
  then, after the response: outbox has 1 message to asha@example.com, subject "Welcome to TaskFlow"

Same request while the mail server is down (send raises ConnectionError)
  -> still 201; the log has "welcome email to asha@example.com failed" with the traceback
```

The fake outbox used by the tests looks like this (copy it into `my-work/` if you want to experiment):

```python
class FakeOutbox:
    def __init__(self, fail=False):
        self.messages, self.fail = [], fail

    def send(self, to, subject, body):
        if self.fail:
            raise ConnectionError("mail server unreachable")
        self.messages.append({"to": to, "subject": subject, "body": body})
```

Note: the test client waits for background tasks before it gives you the response, so the tests can look at the outbox right after the request. A real client gets its answer first.

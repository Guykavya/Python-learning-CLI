## Hint 1

You cannot add a header to a response with a plain function: an ASGI middleware sees *messages*. Which message starts the response, and where would you put `x-request-id`? Wrap `send` in your own function so that you can change that message on its way out.

## Hint 2

```text
if scope["type"] != "http": pass through
incoming = header x-request-id decoded; rid = incoming if VALID_ID.match(incoming) else uuid4().hex
token = request_id_var.set(rid); started = perf_counter(); status = 500
async def send_with_id(message): on "http.response.start": remember status, append (b"x-request-id", rid.encode())
try:    await self.app(scope, receive, send_with_id)
except Exception: log.exception("unhandled error"); send a JSONResponse(500, {"error", "request_id"}) through send_with_id
finally: log "request finished" unless path in QUIET_PATHS; request_id_var.reset(token)
```

The `status` variable is assigned inside the nested function: that needs `nonlocal status`.

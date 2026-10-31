- Adding a handler on every call. Each call adds one more, and each message is printed once per
  handler.
- Removing handlers while looping over `logger.handlers` itself. The list shrinks under the loop
  and every second handler survives.
- Setting the level on the handler only. The logger's own level (default: inherited `WARNING`
  from the root) drops `INFO` before any handler sees it.
- `logging.StreamHandler()` without the stream. It writes to `sys.stderr`.
- Calling `logging.basicConfig(...)` inside the function. That configures the **root** logger
  for the whole program, and does nothing at all on the second call.
- Leaving `propagate` as `True`. Lines appear twice as soon as the root logger has a handler.

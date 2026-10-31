- Forgetting `functools.wraps`. Tracebacks, `help()` and pytest then show `wrapper` instead of
  the real function name.
- Building the message with an f-string and passing one string to `logger.debug`. It works on
  screen, but the text (and every `repr`) is built even when DEBUG is off.
- Checking `logger.level == logging.DEBUG` instead of `isEnabledFor`. A logger with level
  `NOTSET` takes its level from its parent; `isEnabledFor` knows that, `.level` does not.
- `except Exception as exc: ...; raise exc`. Usually fine, but it adds the wrapper line to the
  traceback again; a bare `raise` re-raises exactly what happened.
- Catching the exception and returning `None`. The decorator must never change behaviour: the
  caller still needs the exception.
- Logging the result inside the `try`. If formatting the log line itself raised, it would look
  like the function failed.

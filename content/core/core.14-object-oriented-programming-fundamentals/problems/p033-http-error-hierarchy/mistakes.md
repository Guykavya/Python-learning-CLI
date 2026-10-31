- Forgetting `super().__init__(message)` in a subclass. `str(err)` then shows the raw arguments, or
  nothing, instead of the message.
- Calling `super().__init__(resource, key)`. Then `str(err)` is `"('book', 42)"`.
- `status_for` written as a chain: `if isinstance(err, NotFound): return 404 ...`. A new subclass
  such as `Gone` (410) gets the wrong code until someone edits the chain.
- `except Exception` before `except AppError` in `handle`. The first matching clause wins, so every
  app error becomes a 500.
- A bare `except:` in `handle`. It also catches `KeyboardInterrupt` and `SystemExit`.
- Putting `str(err)` of an unexpected error into the body. Internal messages can contain file paths,
  SQL or passwords.
- Using the hard-coded name `"NotFound"` in `to_dict`. `type(self).__name__` gives the real class.

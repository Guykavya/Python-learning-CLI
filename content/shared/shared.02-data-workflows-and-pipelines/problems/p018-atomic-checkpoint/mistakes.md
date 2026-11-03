- `path.write_text(json.dumps(state))`. It truncates the real file first; a crash leaves it empty.
- `json.dump(state, f)` straight into the real file. A `TypeError` halfway through the state
  leaves a half-written checkpoint and destroys the old one.
- Putting the temp file in `/tmp` or another folder. A rename across file systems is a copy plus
  delete, which is not atomic; `os.replace` simply raises `OSError` when the two paths are on
  different file systems.
- Using `Path.rename` to move into place. On Windows it fails when the target already exists;
  `os.replace` (or `Path.replace`) overwrites on every system.
- Catching only `json.JSONDecodeError`. Bytes that are not UTF-8 raise `UnicodeDecodeError`
  while reading, and `[1, 2]` or `null` are valid JSON that is still not a usable state.
- Deleting the corrupt file. You lose the only evidence of what went wrong.
- Swallowing the problem without a log line. The next run silently starts from the beginning and
  nobody knows why it took four hours.
- Returning `default` itself. The caller mutates the returned state and its default changes.
- Catching `Exception` in `load_checkpoint`. A `PermissionError` (wrong file permissions) is a
  real problem that should stop the run, not be "fixed" by starting over.

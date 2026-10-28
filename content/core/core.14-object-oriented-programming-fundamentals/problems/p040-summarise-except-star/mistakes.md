- Putting the `try` around the whole loop. The first failure then ends the loop and the other tasks
  never run.
- Raising the first error instead of a group, or raising the group even when the list is empty.
- `except Exception: pass` in `run_all`. The failures disappear and the job "succeeds".
- Using `except ValueError:` (without the star) in `summarise`. A plain `except` does not look
  inside a group, so it does not match, and the whole group escapes.
- Thinking only one `except*` clause runs. Each one handles its own part of the group.
- Forgetting `except* Exception`. A `RuntimeError` then escapes from `summarise` as a smaller group.
- Writing `except* KeyError` to also catch `IndexError`. Use `LookupError` if you want both.

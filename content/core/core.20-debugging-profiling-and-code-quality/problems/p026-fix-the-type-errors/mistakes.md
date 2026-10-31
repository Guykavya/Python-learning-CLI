- **Changing the annotation to `dict[str, str]` to make the error go away.** mypy is then happy,
  but `best` still compares strings and `average` crashes. Decide which side is wrong.
- **`# type: ignore` or `Any`.** It hides the message and keeps the bug.
- **Changing `best` to return `""` instead of `None`.** That changes the documented behaviour
  and makes "no scores" look like a player with an empty name.
- **Fixing `best`'s annotation and stopping.** A new error appears in `report`: one fix often
  reveals the next problem. Run the checker again after every change.
- **`if not top:` instead of `if top is None:`.** It works here, but it would also treat a player
  named `""` as missing. Compare with `None` explicitly.
- **Thinking type hints are checked when the code runs.** Python ignores them at run time; only a
  checker like mypy (or your tests) catches the mismatch.

- Taking the **first** frame line. That is the outermost call (usually `<module>`), the place
  where the story started, not where it broke.
- Taking the last frame of the **first** traceback in a chain. The first traceback is the old
  exception; the one that reached you is printed last.
- Matching `File "` anywhere in a line. Source lines are shown under each frame and can contain
  the same words. Anchor at the start of the line and require exactly two spaces.
- Returning the line number as a string. `"6"` is not `6`.
- Making `, in <function>` required. A `SyntaxError` traceback ends with a frame that has no
  function, and your pattern would silently skip to an earlier frame.
- Returning `None` or `()` for text without frames. The task says raise `ValueError`, so the
  caller cannot mistake "nothing found" for an answer.

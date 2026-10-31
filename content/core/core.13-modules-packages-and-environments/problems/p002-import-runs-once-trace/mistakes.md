- Printing `loading counter` twice for the two `import` lines. The second import is answered from
  `sys.modules`; the file is not run again.
- Thinking the second import resets `count` to 0. Nothing in the file runs, so the value stays.
- Thinking `reload` makes a new module object. It reuses the old one, so `counter is old` is `True`.
- Forgetting that `reload` runs `count = 0` again. Module-level state is reset by a reload.

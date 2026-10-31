- Thinking `from settings import level` makes `level` an alias of `settings.level`. It copies the binding
  once; later rebinding on either side is not seen by the other.
- Thinking `bump()` changes `main.level`. `global` refers to the module where the function was defined.
- Thinking `level = 99` changes `settings.level`.
- Mixing up mutation and rebinding: `append` changes the shared list, `settings.names = [...]` does not
  touch the list that `main.names` points to.
- Printing `11 11` on the last line. `bump()` returns 11, but `main.level` is still the 10 copied just before.

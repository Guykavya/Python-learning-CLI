- Writing `parent after ['start', 'parent', 'one']`. The child appended to its own copy in its
  own memory.
- Leaving out the second and third `loading module as ...` lines. With spawn, every child
  imports the script and runs its top-level code.
- Writing `loading module as __main__` for the children. A spawned child imports your script
  under the name `__mp_main__`, so the guard is false there.
- Expecting the second child to see `'parent'` and `'main'`. A spawned child is built from a
  fresh import, not from the parent's current state.
- Thinking `child("main")` runs in a new process. Without `Process(...)`, it is an ordinary
  function call in the parent, and it really changes the parent's list.
- Forgetting `exit code 0`, or writing `None`. After `join()` the exit code is known.

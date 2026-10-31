- Printing `registry runs` more than once before the reload. A module runs only on its first import.
- Thinking `count += 100` in `b` changes `registry.count`. It rebinds the name `count` in `b` only.
- Thinking `items.append` in `b` works on a copy. `from registry import items` shares the same list.
- Thinking `reload` makes a new module object, or updates `b.items`. It runs the file again in the
  same module object; names copied into other modules still point at the old objects.
- Thinking `b.add` still uses the old list. The old function reads `items` from the module's globals
  dictionary when it runs, and that dictionary now holds the new list.

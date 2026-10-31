## Hint 1

Before Python searches any folder, it looks in one dictionary. Which one, and what is in it after the
first import? Then: which folders does it search, and in which order?

## Hint 2

Answer in order: (1) check `sys.modules` → search `sys.path` → new module object → store it in
`sys.modules` → run the file top to bottom → bind the name; (2) second time: found in `sys.modules`, nothing
runs; (3) `"temps"` vs `"__main__"`; (4) the `if __name__ == "__main__":` block; (5) tests, `input()`, slow work.

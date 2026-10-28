## Hint 1

Try the starter on two logs in a row and read `report.txt` after each call. What does mode `"w"` do? Look at the last `write`: does it end with a newline? Which lines does `startswith` find? Who closes the files?

## Hint 2

Four fixes: (1) open `dst` with `"a"`; (2) write `f"errors={count}\n"`; (3) test `"ERROR" in line`; (4) use `with open(...) as f:` for both files, so they are closed.

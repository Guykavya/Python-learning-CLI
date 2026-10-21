## Hint 1

`line.split()` turns `"add 5"` into `["add", "5"]`. A pattern like `case ["add", n]:` matches
exactly that shape and captures `"5"` in `n`.

## Hint 2

`case ["add" | "sub"]:` matches the command with no number. `case []:` matches a blank line.

## Hint 3

Put everything in `while True:`. `case ["quit"]:` should `break`. The wildcard reports
unknown commands.

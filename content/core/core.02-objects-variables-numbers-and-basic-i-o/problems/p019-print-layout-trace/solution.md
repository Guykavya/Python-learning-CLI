## Walkthrough

1. Default `sep=" "`: `1 2 3`.
2. `sep=""`: `123`.
3. `a--b` then `end="|"` instead of a newline, so the line stays open.
4. `print("c")` continues the same line: `a--b|c`.
5. `x` with `end=""`: the line stays open.
6. `y,z` follows directly: `xy,z`.
7. `sep="\n"` puts a newline between 10 and 20: two lines.
8. `total:` + ` = ` + `10`: `total: = 10`.
9. `ABC` with `end="!\n"`: `ABC!`.

## The rule

`print(*items, sep=" ", end="\n")` writes the items with `sep` between them and then writes `end`.
Nothing else is added.

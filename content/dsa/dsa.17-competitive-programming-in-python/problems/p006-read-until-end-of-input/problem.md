# Read until end of input

Some problems do not tell you how many lines follow: you read until the input ends (EOF, "end of file").

Each line holds zero or more integers separated by spaces. For **every line** print the sum of its numbers (a blank line has sum `0`). After the last line print `total: S`, where `S` is the sum of all numbers.

The input may have trailing spaces, blank lines, Windows line endings (`\r\n`), and the last line may or may not end with a newline. An empty input prints just `total: 0`.

## Example

```text
1 2
(blank line)
3 
```
(the last line is `3` followed by a space)

```text
3
0
3
total: 6
```

## Hints about the tools

`for line in sys.stdin:` and `sys.stdin.read().splitlines()` both read to the end. A blank line is a line like any other, so it must produce a `0`.

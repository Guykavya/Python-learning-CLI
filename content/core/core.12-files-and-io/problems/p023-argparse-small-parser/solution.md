## Approach

Build the parser inside the function, add the four arguments, and call `parser.parse_args(argv)` with the list you were given. `nargs="+"` means one or more, `action="store_true"` makes a flag, `type=int` converts and checks the number, and `choices` restricts the values. argparse prints a usage message to stderr and raises `SystemExit(2)` for wrong input.

## Code

```python
import argparse


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="tidy")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--mode", choices=["copy", "move"], default="copy")
    return parser.parse_args(argv)
```

## Complexity

O(number of arguments).

## Another way

Create the parser once at module level in a `build_parser()` function, and call `build_parser().parse_args(argv)`. That is how larger tools keep the parser testable. `parse_args(None)` reads `sys.argv[1:]`.

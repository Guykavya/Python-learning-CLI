## Walkthrough

| Expression | Result | Why |
|---|---|---|
| `"a  b".split(" ")` | `['a', '', 'b']` | two spaces, two cuts, empty piece between |
| `"a  b".split()` | `['a', 'b']` | whitespace runs count as one |
| `"  x ".split()` | `['x']` | ends ignored |
| `"".split()` | `[]` | no words |
| `"".split(",")` | `['']` | one empty field |
| `"a,b,,c,".split(",")` | `['a', 'b', '', 'c', '']` | every comma cuts, including the last |
| `"1-2-3-4".split("-", 2)` | `['1', '2', '3-4']` | at most two cuts from the left |
| `"1-2-3-4".rsplit("-", 1)` | `['1-2-3', '4']` | one cut from the right |
| `"x\ny\n".split("\n")` | `['x', 'y', '']` | the final newline cuts too |
| `"x\r\ny\n".splitlines()` | `['x', 'y']` | `\r\n` is one line break; no empty last piece |
| `len("one two  three".split(" "))` | `4` | the double space adds an empty piece |
| `"-".join("a b  c".split())` | `a-b-c` | clean words joined |

## Approach

`self` is just the object the method was called on (chapter section 3). Track the objects, not the
names:

| Line | Long form | a (also c) | b | Printed |
|---|---|---|---|---|
| `a.tick()` | `Counter.tick(a)` | 1 | 10 | |
| `a.tick(5)` | `Counter.tick(a, 5)` | 6 | 10 | |
| `print(b.tick())` | `Counter.tick(b)` | 6 | 11 | `11` |
| `b.show()` | | 6 | 11 | `b = 11` |
| `a.show()` | | 6 | 11 | `a = 6` |
| `c.tick(100)` | `c` is `a` | 106 | 11 | |
| `a.show()` | | 106 | 11 | `a = 106` |
| `print(c is a, b is a)` | | | | `True False` |
| `Counter.tick(b, 2)` | `self` is `b` | 106 | 13 | |
| `b.show()` | | 106 | 13 | `b = 13` |
| `b.reset()` | | 106 | 0 | |
| `print(a.count, b.count, c.count)` | | | | `106 0 106` |
| `r()` | `a.tick()` | 107 | 0 | |
| `print(a.count)` | | | | `107` |
| `print(a.name, c.name)` | | | | `a a` |

## Output

```text
11
b = 11
a = 6
a = 106
True False
b = 13
106 0 106
107
a a
```

## Complexity

Not applicable.

## Another way

Put `print("self is", self.name)` at the start of `tick` and run the program. Each line tells you
which object the call is working on. To make `c` a real second counter, write
`c = Counter(a.name, a.count)`.

# Counter commands

A counter starts at 0. Read commands, one per line, until `quit`. Each command is split into
words:

| Command | Effect |
|---|---|
| `add N` | add the whole number N (may be negative) |
| `sub N` | subtract N |
| `double` | multiply the counter by 2 |
| `reset` | set it back to 0 |
| `show` | print `Counter: <value>` |
| `add` or `sub` with no number | print `Missing number` |
| a blank line | ignored |
| `quit` | stop, and print `Final: <value>` |
| anything else | print `Unknown command: <the line, stripped>` |

Commands are lower case. You may assume that when a number is given, it is a valid whole
number.

**Example**

Input:
```
add 5
double
sub 3
show
add
fly away
quit
```
Output:
```
Counter: 7
Missing number
Unknown command: fly away
Final: 7
```

**Rule for this problem:** use `match` on the list of words with sequence patterns.

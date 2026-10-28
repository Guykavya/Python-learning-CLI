## Approach

Lookup reads the instance first, then the class; assignment always writes to the instance
(chapter section 5). Track the three boxes:

| Line | Class `Player` | `p` own attrs | `q` own attrs | Printed |
|---|---|---|---|---|
| start | team red, lives 3, badges [] | name | name | |
| `print(p.team, q.team)` | | | | `red red` (both from the class) |
| `p.team = "blue"` | | + team blue | | |
| print | | | | `blue red red` |
| `Player.team = "green"` | team green | | | |
| print | | | | `blue green` (p's own value hides the class) |
| `p.lose_life()` | lives 3 | + lives 2 | | read 3 from class, write 2 to p |
| print | | | | `2 3 3` |
| `vars` check | | | | `True False` |
| `q.earn("gold")` | badges ['gold'] | | | append to the shared class list |
| print | | | | `['gold'] 1` (p sees the same list) |
| `p.badges = ["silver"]` | | + badges ['silver'] | | |
| `p.earn("bronze")` | | badges ['silver', 'bronze'] | | `self.badges` now finds p's own list |
| print | | | | `['silver', 'bronze'] ['gold']` |
| `del p.team` | | − team | | |
| `print(p.team)` | | | | `green` (from the class again) |

## Output

```text
red red
blue red red
blue green
2 3 3
True False
['gold'] 1
['silver', 'bronze'] ['gold']
green
```

## Complexity

Not applicable.

## Another way

Print `vars(p)`, `vars(q)` and `Player.badges` after every step and compare with your table. The
`badges` line is the famous trap: a mutable class attribute is shared by **all** instances. The fix
is to create the list in `__init__`: `self.badges = []`.

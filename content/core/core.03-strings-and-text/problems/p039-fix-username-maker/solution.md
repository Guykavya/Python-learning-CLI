## Approach

Fix one symptom at a time and compare each line with the specification. Do not guess.

## The bugs

| Starter line | Bug | Effect |
|---|---|---|
| `year = input()` | not stripped | `" 2005"[-2:]` is fine, but `int` and slicing on unstripped text is fragile; `"2005 "[-2:]` is `"5 "` |
| `words = name.split(" ")` | explicit separator | double spaces give empty words, and `""[0]` crashes |
| `last = words[1]` | second word, not last | middle names give the wrong letter |
| `first.lower()` | result thrown away | the username keeps capitals |
| `last[0]` | not lowercased | `KUMAR` gives `K` |
| `year[:-2]` | wrong slice | gives the first two digits, `20` |
| `name.title()` | uses the raw name | extra spaces stay in the greeting |
| `"Age in 2026: " + 2026 - int(year)` | str plus int | `TypeError` crash |

## Fixed code

```python
name = input()
year = input().strip()
words = name.split()
first = words[0].lower()
last = words[-1]
username = first + last[0].lower() + year[-2:]
print(f"Hello, {' '.join(words).title()}!")
print(f"Username: {username}")
print(f"Age in 2026: {2026 - int(year)}")
```

## Lesson

Half of these bugs do not crash. They produce believable but wrong text. That is why tests compare exact output, and why `repr()` is so useful when debugging strings.

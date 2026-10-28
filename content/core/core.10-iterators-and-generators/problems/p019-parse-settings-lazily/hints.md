## Hint 1

You need the line number for the error message. Which built-in gives you a counter and the
item together, and how do you make it start at 1?

## Hint 2

Clean the line with `.strip()` first. Then a blank line becomes `""` and a comment line
starts with `"#"`. Which string method splits only at the first `=`?

## Hint 3

```
for number, line in enumerate(lines, start=1):
    text = line.strip()
    if text is empty or starts with "#": continue
    if "=" not in text: raise ValueError(f"line {number}: missing '='")
    key, value = text.split("=", 1)
    yield key.strip(), value.strip()
```

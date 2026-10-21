## Approach

Accumulate words into a current line. Flush (print) it when the next word does not fit. Flush
once more after the loop.

## Code

```python
width = int(input())
words = input().split()
line = ""
count = 0
for word in words:
    if not line:
        line = word
    elif len(line) + 1 + len(word) <= width:
        line += " " + word
    else:
        print(line)
        count += 1
        line = word
if line:
    print(line)
    count += 1
print(f"Lines: {count}")
```

## Why `len(line) + 1 + len(word)`

The `1` is the space between the line and the new word. Leaving it out lets lines grow one
character too long.

## The final flush

As in run-length encoding, a line is only printed when something comes after it that does
not fit. The last line has nothing after it, so the loop never prints it. This "flush after
the loop" step belongs to every grouping loop.

## Why an empty `line` starts with the word

A word longer than `W` would never fit, so without this case it would never be placed. An empty
line always accepts the next word.

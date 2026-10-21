## Approach

A sentinel loop: read, check for the stop word, then use the value. The loop-and-a-half
(`while True` with `break`) reads in one place only.

## Code

```python
count = 0
total = 0.0
while True:
    line = input().strip()
    if line.lower() == "done":
        break
    count += 1
    total += float(line)
print(f"Items: {count}")
print(f"Total: {total:.2f}")
```

## Why the check comes before the use

If you added `float(line)` first, the word `done` would be converted and crash. The sentinel
is a signal, not data, so it must be caught before any processing.

## Another way

Read once before the loop and again at the bottom:

```python
line = input().strip()
while line.lower() != "done":
    count += 1
    total += float(line)
    line = input().strip()
```

## Hint 1

Think of it as a pipeline of small steps: number the lines, keep the matching ones, clean
them, stop after enough. Which built-in numbers items? Which itertools tool stops after
a fixed number of items without reading one more?

## Hint 2

Lower-case both sides to compare: `word.lower() in line.lower()`. Build a generator
expression of matches. What does `islice(matches, None)` do?

## Hint 3

```
target = word.lower()
numbered = enumerate(lines, start=1)
matches = ((n, line.rstrip()) for n, line in numbered if target in line.lower())
yield from islice(matches, max_count)
```

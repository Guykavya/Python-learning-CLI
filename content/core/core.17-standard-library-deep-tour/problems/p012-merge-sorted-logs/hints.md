## Hint 1

`heapq.merge(a, b, c)` already returns a lazy iterator. What does it compare by default? With `"... 10:00:05 zzz"` from the first source and `"... 10:00:05 aaa"` from the second, which comes first if the **whole line** is compared? Which `key=` makes it compare only the timestamp?

## Hint 2

`heapq.merge` is stable: with equal keys, items from earlier iterables come first. For the files, open each one in a `with` block (or keep a list of open files and close them all at the end), and strip the `"\n"` from each line before merging so a missing final newline does not matter. Then write `line + "\n"`.

## Hint 3

```
def ts(line): return line[:19]

merge_logs(*sources): return heapq.merge(*sources, key=ts)

merge_files(paths, out_path):
    files = [open(p, encoding="utf-8") for p in paths]
    try:
        cleaned = [(l.rstrip("\n") for l in f) for f in files]
        count = 0
        with open(out_path, "w", encoding="utf-8") as out:
            for line in merge_logs(*cleaned):
                if line.strip(): out.write(line + "\n"); count += 1
    finally:
        close every file
    return count
```
(If you skip blank lines **before** merging, they never reach the key function.)

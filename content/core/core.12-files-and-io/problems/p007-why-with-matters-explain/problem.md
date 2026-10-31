# Explain: why `with` matters

Meera wrote this code to save a score list:

```python
def save_scores(path, scores):
    f = open(path, "w")
    for s in scores:
        f.write(f"{s}\n")
    # the program ends here, no close()
```

Her friend says: "Sometimes the file is empty or cut off after a crash. Use `with`." Meera asks:
"But the data was written. Why would anything be lost? What does `with` do that I do not?"

In `answer.md` (about 150 to 300 words), explain:

1. What **buffering** is, and why `write()` does not always put the bytes on disk at once.
2. What can happen to buffered data if the file is **never closed** and the program crashes or is killed.
3. What a `with` block does when it ends, in the normal case **and** when an error is raised inside it.
4. Two other problems of a forgotten `close()` besides lost data (think of many files in a loop, or other programs).
5. What the `with` version of her function looks like.

# Explain: why save to a temp file, then replace

Dev wrote a function that saves the settings of his app:

```python
def save_settings(path, text):
    with open(path, "w") as f:
        f.write(text)
```

A senior colleague says: "Never do that for important files. Write to a temporary file in the same folder
and then call `os.replace`."

In `answer.md` (about 150 to 300 words), explain:

1. What happens to the old content of `path` the moment `open(path, "w")` runs, and what the file looks like
   if the program or the computer crashes in the middle of `f.write`.
2. How the temp-file way fixes it. What do readers of `path` see at every moment?
3. What **atomic** means for `os.replace`, and why the temp file must be in the **same folder** (the same disk)
   as `path`.
4. One more step that makes the save safer, and one thing that this pattern still cannot protect against.

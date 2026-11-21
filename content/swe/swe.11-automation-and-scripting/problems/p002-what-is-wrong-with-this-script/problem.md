# What is wrong with this script?

Chapter sections 2.1 (a first script, and what is wrong with it), 2.2 (the skeleton to copy), 2.3 (exit codes), 2.4 (stdout, stderr and the pipe) and "Try it: what is wrong?". A colleague wrote this to file their PDFs and wants to run it from cron every night:

```python
# bad_tidy.py   (do not run on a real folder)
import os, shutil
folder = "C:/Users/me/Downloads"
for f in os.listdir(folder):
    if f.endswith(".pdf"):
        try:
            shutil.move(folder + "/" + f, "pdfs/" + f)
        except Exception as e:
            print("could not move", f, e)
print("done")
```

In `answer.md`, for **each** of the problems below say (a) what actually goes wrong, with a concrete situation, and (b) the fix from the chapter. One short paragraph each is enough.

1. The folder is written in the code.
2. There is no dry run (and no journal to undo).
3. Errors are reported with `print`.
4. The script exits with code 0 even when moves failed.
5. `"pdfs/" + f` is relative: it works only when started from one particular folder.
6. Paths are glued with `+` and `"/"`.
7. The move can overwrite an existing file.
8. Name **one more** problem the list above does not mention.

Finish with the skeleton you would give your colleague (the shape of section 2.2, in about 15 lines of code or pseudocode).

## Example

A good paragraph for 3: "`print` writes to stdout, the same stream as the tool's data. Under cron nobody reads stdout, and if someone runs `bad_tidy.py | wc -l` the error lines are counted as results. Send diagnostics to stderr with `logging` (`log.error(...)`), so data and messages stay separate and the log file keeps them with a timestamp."

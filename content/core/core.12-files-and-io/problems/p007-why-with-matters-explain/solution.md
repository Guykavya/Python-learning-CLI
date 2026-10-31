## Approach

Start from one idea: `write()` talks to a buffer, and only `flush()` or `close()` talks to the disk. `with` is the tool that makes sure `close()` always runs.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Try it: write a file without `with` and without `close()`, then kill the program with `os._exit(0)` before it ends, and look at the file. Compare with the `with` version.

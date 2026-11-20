## Approach

```python
def _is_start(line):
    return line.startswith("<<<<<<<") and (len(line) == 7 or line[7] == " ")


def _is_end(line):
    return line.startswith(">>>>>>>") and (len(line) == 7 or line[7] == " ")


def resolve(text, choose):
    if not callable(choose) and choose not in ("ours", "theirs", "both"):
        raise ValueError(f"choose must be 'ours', 'theirs', 'both' or a function, not {choose!r}")
    out = []
    state = 0          # 0 outside, 1 in our part, 2 in their part
    start = 0
    ours = []
    theirs = []
    for n, line in enumerate(text.split("\n"), 1):
        if state == 0:
            if _is_start(line):
                state, start, ours, theirs = 1, n, [], []
            elif _is_end(line):
                raise ValueError(f"line {n}: '>>>>>>>' without a matching '<<<<<<<'")
            else:
                out.append(line)
        else:
            if _is_start(line):
                raise ValueError(f"line {n}: a second '<<<<<<<' inside the block that began at line {start}")
            if line == "=======":
                if state == 2:
                    raise ValueError(f"line {n}: a second '=======' in the block that began at line {start}")
                state = 2
            elif _is_end(line):
                if state == 1:
                    raise ValueError(f"line {n}: '>>>>>>>' before '=======' in the block that began at line {start}")
                if callable(choose):
                    out.extend(choose(list(ours), list(theirs)))
                elif choose == "ours":
                    out.extend(ours)
                elif choose == "theirs":
                    out.extend(theirs)
                else:
                    out.extend(ours + theirs)
                state = 0
            elif state == 1:
                ours.append(line)
            else:
                theirs.append(line)
    if state != 0:
        raise ValueError(f"line {start}: the conflict block that begins here is never closed")
    return "\n".join(out)
```

A small state machine: `state` is 0 outside a block, 1 while collecting our lines, 2 while collecting theirs. At `>>>>>>>` the block is complete and the chosen lines are appended to the output. `choose` receives **copies** of the two lists, so a function cannot change the parser's data.

Example (`"both"`): the line `<<<<<<< HEAD` starts state 1 at line 2; `B = 2` goes to `ours`; `=======` switches to state 2; `B = 3` goes to `theirs`; `>>>>>>> feature` writes `B = 2`, `B = 3` and goes back to state 0.

## Complexity

`O(number of lines)`.

## Another way

`git checkout --ours file` and `--theirs file` pick a whole side without editing the markers (chapter section 6.5), and `git merge-file` merges three versions. A tool like this is what an editor's "accept current / accept incoming" buttons do for each block.

## Why it matters

Every unresolved marker that reaches a commit breaks the code (the file is no longer valid Python). Checking for leftover markers in CI (and in p010's `finish_merge`) protects the history.

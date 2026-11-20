## Hint 1

When the naive version opens `path` with `"wb"`, the old file is emptied at once. Where could you write instead, so that the final name is untouched until the new content is complete? Which single call swaps a finished file into place?

## Hint 2

```text
build_report: header; for row in sorted(rows): [month, *row]; return text.encode("utf-8")

write_atomic(path, data, crash):
    tmp = f"{path}.{os.getpid()}.tmp"            # same folder as path
    with open(tmp, "wb") as f:
        write first half; crash.hit("mid-write"); write second half
        f.flush(); os.fsync(f.fileno())
    crash.hit("before-replace")
    os.replace(tmp, path)
```

**1. The problem with `"w"`.** Opening a file in mode `"w"` **empties it at once**, before the first byte of the
new text is written. If the program crashes (an exception, a power cut, a full disk) during `write`, the file is
left empty or half written. The old good settings are gone and the new ones are not complete.

**2. The temp-file way.** Write all new content to a temporary file next to the real one, for example
`settings.json.tmp`. The real file is not touched while this happens. If anything fails, you delete the temp
file and `path` still has the old, complete content. When the temp file is complete, you call
`os.replace(temp, path)`. A reader sees either the whole old file or the whole new file, never something in
between.

**3. Atomic and same folder.** Atomic means the operation happens fully or not at all, and no other process can
see a half-done state. `os.replace` on one disk only changes a name in the directory, so it is atomic and
fast. If the temp file were on another disk, the system would have to copy the data, which is slow, can fail in
the middle, and is not atomic. `os.replace` also overwrites an existing target on every system, unlike
`os.rename` on Windows.

**4. More safety and limits.** Call `f.flush()` and `os.fsync(f.fileno())` before the replace, so the data is on
the disk and not only in a memory buffer. The pattern still cannot help if two programs write the same file at
the same time and each replaces the other's work (lost update), or if the new content itself is wrong.

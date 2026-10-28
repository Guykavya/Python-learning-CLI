## Hint 1

Follow the content of the file after every `with` block. What does `"w"` do to an old file at the moment of
`open`, before any `write`?

## Hint 2

Text written with `f.write` goes into a buffer first. The size on disk grows when the buffer is flushed,
and `close()` (the end of the `with` block) flushes it.

```
"a": tell() right after the write = size of the file so far + new text
"w": size is 0 right after open, still 0 after a small write (buffer), 4 after close
"x": raises FileExistsError because the file is already there
"r": f.write raises io.UnsupportedOperation; the read returns the text; a second read returns ""
```

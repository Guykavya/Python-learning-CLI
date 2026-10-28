## Approach

1. Mode `"w"` creates the file with `one` and `two`. The list is `['one', 'two']`.
2. Mode `"a"` adds `three\n` at the end. The file had 8 bytes, the new text has 6: `tell()` is `14`.
3. Mode `"w"` on an existing file **empties it at once**. The first size is `0`. After `f.write("new\n")` the
   text is still in Python's buffer, so the size is `0` again. After the `with` block closed the file, the
   size is `4`.
4. Mode `"x"` means "create, and fail if it exists". It raises `FileExistsError`, so `exists` is printed.
   The `write` is never reached.
5. Mode `"r"` opens a file that can only be read. `f.write` raises `io.UnsupportedOperation`.
   The type name is `UnsupportedOperation`. Then the whole content is read. The next `read()` is at the
   end of the file and returns an empty string, so the comparison is `True`.

## Output

```text
['one', 'two']
14
['one', 'two', 'three']
0
0
4
['new']
exists
UnsupportedOperation
['new']
True
```

## Complexity

Not applicable.

## Another way

Call `f.flush()` after the write in step 3 and print the size again. It becomes `4` before the `with` block ends.

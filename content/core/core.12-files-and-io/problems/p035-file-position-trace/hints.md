## Hint 1

Write the file content as a string and draw a number line under it. After the first `with`, what is the file
content? What did `f.write("klm\n")` do to the position and to the content?

## Hint 2

Keep a table of (content, position) after every line of the first block.

```
content "abcdef\nghij\n" (12 chars), pos 0
read(3)       -> "abc", pos 3
seek(0, 2)    -> pos 12 (end)
write("klm\n")-> content is 16 chars, pos 16
seek(0); readline() -> "abcdef\n", pos 7
seek(2); write("XY") -> overwrites two characters, it does NOT insert
```

For `"a"`: the position at open is the end. After `seek(0)` a write still goes to the end.
For the failing block: the `write` before the error is kept, `with` closes the file, `f` is still a name.

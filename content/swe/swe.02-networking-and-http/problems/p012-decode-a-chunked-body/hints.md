## Hint 1

You read a line (the size), then exactly that many bytes, then expect `\r\n`. Which two kinds of reading does that need: "up to the next CRLF", and "exactly n bytes"? Keep a position `pos` in the data.

## Hint 2

The size line may have an extension: take the part before the first `;`. Check the text with a regular expression for hex digits before calling `int(x, 16)`, because `int` also accepts `0x4`, `+4` and `1_0`.

## Hint 3

```text
loop:
    find CRLF from pos; no CRLF -> error
    size text = line before ";" stripped; must be hex digits -> else error
    size == 0 -> break
    take data[pos:pos+size] (must be complete); then expect CRLF
after the 0 chunk: read lines until an empty line; each "name: value" goes into trailers
```

## Hint 1

The naive loop prints each chunk as it is: copy the four chunks, in the form `print` shows bytes. A byte such as `\x05` stays `\x05` inside `b'...'`.

## Hint 2

For the framed receiver, keep `buf` after each chunk. Chunk 1 gives `\x05HEL`: the length byte says 5 but only 3 bytes follow, so nothing is printed. Chunk 2 adds `LO\x07WORLD!`, so `buf` becomes `\x05HELLO\x07WORLD!`.

## Hint 3

After chunk 2: `HELLO` is complete (print it), then `buf = \x07WORLD!`: needs 7 bytes but has 6, so `break`. Chunk 3 adds `!\x03BY`: `WORLD!!` completes; then `\x03BY` needs 3 and has 2: wait. Chunk 4 `E` completes `BYE`.

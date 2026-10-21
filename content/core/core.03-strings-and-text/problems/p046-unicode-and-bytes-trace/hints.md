## Hint 1

`é` is code point 233, which is `e9` in hex. In UTF-8 it takes two bytes, `c3 a9`. How does Python display a byte above 127 inside `b'...'`?

## Hint 2

Indexing `bytes` gives an **int**. Slicing gives `bytes`. `0xc3` is 195.

## Hint 3

A `bytearray` prints as `bytearray(b'...')`. Text and bytes are never equal, even with the same letters.

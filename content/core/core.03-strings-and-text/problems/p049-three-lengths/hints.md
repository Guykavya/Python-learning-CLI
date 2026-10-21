## Hint 1

Code points, bytes, and what a human sees (grapheme clusters). Print `[f"U+{ord(c):04X}" for c in s]` for each string to see the code points.

## Hint 2

A flag is two "regional indicator" code points. The family is three people joined by "zero width joiner" (U+200D) characters. The word uses `e` plus a combining accent. Each code point above U+FFFF takes 4 UTF-8 bytes; U+200D takes 3; U+0301 takes 2.

## Hint 3

Slicing works on code points, so it can separate a base letter from its accent, or split a family into people. Cutting bytes can split a single code point, giving invalid UTF-8. NFC can combine `e` + accent into `é`, but there is no single code point for a family or a flag.

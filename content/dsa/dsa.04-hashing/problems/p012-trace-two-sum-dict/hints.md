## Hint 1

First call: target 8. At `i = 0`, `x = 4`, `need = 4`, and `seen` is empty, so no pair; then `seen = {4: 0}`.

## Hint 2

The line prints `need` and `seen` **before** testing. Walk to `i = 5`, `x = 3`, `need = 5`: `5` was stored at index 4.

## Hint 3

Second call: `[3, 3]`, target 6. At `i = 1`: `need = 3`, `seen = {3: 0}`, so the pair is `0 1`.

## Hint 1

`update(i, v)`: the block of `i` is `i // B`; change its sum by `v - a[i]`, then store `v`.

## Hint 2

`query`: three loops. Walk `l` forward element by element until `l` is at a block start (`l % B == 0`) or reaches `r`. Then, while a whole block fits (`l + B <= r`), add `blocks[l // B]` and jump `l += B`. Finally walk the rest element by element. Count one step per element and per block.

## Hint 3

A query adds at most `B - 1` elements on each side and at most `n / B` blocks: `O(B + n / B)`, which is smallest when `B = sqrt(n)`.

## Approach

Follow the four rules token by token, writing both rows after each token. Numbers go straight to the output. An operator first releases every operator on top with higher or equal precedence (stopping at a `(` or a lower one). `)` releases everything down to its `(`.

## Expected output

```text
3 | out: 3 | ops: 
+ | out: 3 | ops: +
4 | out: 3 4 | ops: +
* | out: 3 4 | ops: + *
2 | out: 3 4 2 | ops: + *
/ | out: 3 4 2 * | ops: + /
( | out: 3 4 2 * | ops: + / (
1 | out: 3 4 2 * 1 | ops: + / (
- | out: 3 4 2 * 1 | ops: + / ( -
5 | out: 3 4 2 * 1 5 | ops: + / ( -
) | out: 3 4 2 * 1 5 - | ops: + /
end | out: 3 4 2 * 1 5 - / +
```

## Why

- At `/`, the `*` (precedence 2, equal) leaves, because `4 * 2` must be done before dividing: left to right. Then the top is `+` (precedence 1, lower): it stays.
- After `(`, the `-` is pushed on top of `(`; the loop stops at the `(` so the `/` waits.
- At `)`, only the `-` leaves, then the `(` is dropped. The stack is back to `+ /`.
- At the end the stack is emptied from the top: first `/`, then `+`.

The postfix `3 4 2 * 1 5 - / +` means `3 + ((4 * 2) / (1 - 5))` = `3 + 8 / -4` = `3 + (-2)` = `1`.

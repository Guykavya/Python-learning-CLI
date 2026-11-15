## Hint 1

`arr[i]` is the minimum of a subarray exactly when the subarray stays strictly between `p` and `q`. It can start at any of `p + 1 .. i` (that is `i - p` choices) and end at any of `i .. q - 1` (`q - i` choices). How do you find `p` for every `i` with one stack pass?

## Hint 2

Two passes:

```
left to right: pop while arr[top] >= arr[i];  prev[i] = top or -1;  push i
right to left: pop while arr[top] >  arr[i];  nxt[i]  = top or n;   push i
answer = sum(arr[i] * (i - prev[i]) * (nxt[i] - i)) % (10**9 + 7)
```

(Python integers do not overflow, so you may take the modulo once at the end; in other languages you take it at every step.)

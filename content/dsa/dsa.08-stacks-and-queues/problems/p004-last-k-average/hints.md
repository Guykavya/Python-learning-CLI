## Hint 1

`window = deque(maxlen=k)` drops the oldest item automatically when you append to a full deque. But your running total does not know about that drop. How can you find out, **before** appending, which value is about to disappear?

## Hint 2

When `len(window) == k`, the value about to be dropped is `window[0]`.

```
for x in values:
    if len(window) == k: total -= window[0]
    window.append(x); total += x
    out.append(total / len(window))
```

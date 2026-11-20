## Hint 1

If the numbers of one test case can be on several lines, what unit of input is always safe to read: a line or a whitespace-separated token?

## Hint 2

Read **all** the text once, split it into tokens, and walk through the list with an index (or an iterator). Each test case consumes one token for `n`, then exactly `n` tokens.

## Hint 3

```text
it = iter(sys.stdin.read().split())
t = int(next(it))
repeat t times:
    n = int(next(it))
    a = [int(next(it)) for each of n]
    total = sum(a)
    answer = how many x have x * n > total
collect answers, print them joined by newlines
```

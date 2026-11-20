# Sum of numbers with `sys.stdin`

You are given `n` integers, one per line. Print their sum.

## Input

The first line holds `n` (`1 <= n <= 2 * 10**5`). Each of the next `n` lines holds one integer `x` (`|x| <= 10**9`).

## Output

One line: the sum.

## Example

```text
3
5
-2
10
```
```text
13
```

## The catch

On a real judge a loop of `n` calls to `input()` is slow. The tests of this problem count how often your program calls `input()` on a large input. **Calling it more than 1000 times fails** with a message. Read the whole input at once with `sys.stdin` instead (chapter section 4).

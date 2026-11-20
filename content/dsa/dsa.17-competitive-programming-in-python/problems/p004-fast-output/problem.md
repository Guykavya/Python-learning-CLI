# Fast output

Read `n` integers and print the square of each, one per line.

## Input

`n` (`1 <= n <= 2 * 10**5`) on the first line, then `n` integers `x` (`|x| <= 10**6`) separated by whitespace (they may be on one line or many).

## Output

`n` lines: `x * x` for each number, in order.

## Example

```text
4
3 -2 0 10
```
```text
9
4
0
100
```

## The catch

Calling `print` 2·10^5 times is slow. The tests count how many times your program writes to standard output on a large input. **More than 1000 writes fails.** Collect the lines in a list, then write them once (chapter section 5).

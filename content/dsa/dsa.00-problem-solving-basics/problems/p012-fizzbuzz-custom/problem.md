# FizzBuzz with your own numbers

Read three integers `a`, `b` and `n`, each on its own line. Then, for every `i` from 1 to `n`, print one line:

- `FizzBuzz` if `i` is divisible by both `a` and `b`,
- `Fizz` if `i` is divisible by `a` but not by `b`,
- `Buzz` if `i` is divisible by `b` but not by `a`,
- otherwise the number `i` itself.

The words are case-sensitive: capital `F` and `B`, no spaces.

## Input

Three lines:

1. the integer `a`
2. the integer `b`
3. the integer `n`

## Output

Exactly `n` lines, one for each `i` from 1 to `n`. If `n` is 0, print nothing.

## Examples

Input `a = 3`, `b = 5`, `n = 15`:

```
3
5
15
```

Output:

```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

Input `a = 2`, `b = 2`, `n = 4` (when `a` and `b` are equal, every multiple is divisible by both):

```
2
2
4
```

Output:

```
1
FizzBuzz
3
FizzBuzz
```

Input `a = 1`, `b = 4`, `n = 4` (every number is divisible by 1):

```
1
4
4
```

Output:

```
Fizz
Fizz
Fizz
FizzBuzz
```

## Constraints

- `1 <= a <= 10^5` and `1 <= b <= 10^5`
- `0 <= n <= 10^5`

Use `input()` without a prompt message.

## Before you code

Decide the order of your `if` checks. Try your plan on `i = 15` with `a = 3`, `b = 5`. Which check must come first?
Write your plan as comments at the top of `solution.py`.

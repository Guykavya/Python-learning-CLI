## Walkthrough

1. `t1` passes: `4 == 4`.
2. `t2` fails: `"ABC" != "abc"`, the message is printed.
3. `t3` **passes**. The assert checks a tuple with two items. A non-empty tuple is always true, so this assert can never fail. Python warns about it at compile time.
4. `t4` fails: an empty list is falsy, so the condition is false.
5. `t5`: the first assert passes, the second fails because `0.1 + 0.2` is `0.30000000000000004`.
6. `t6` fails with `x was 5`: `5 < 5` is false.
7. `t7` passes: `not ""` is `True`.
8. `t8`: equal lists pass, but two separate list literals are two different objects, so `is` fails with `same object`.
9. `t9` passes: the difference is far smaller than 1e-9.

## The exact output

```text
1 passed
2 FAILED: upper changes the case
3 passed
4 FAILED: an empty list is falsy
5 FAILED: float sum
6 FAILED: x was 5
7 passed
8 FAILED: same object
9 passed
```

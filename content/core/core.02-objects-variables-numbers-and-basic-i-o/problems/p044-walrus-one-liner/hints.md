## Hint 1

`(name := expression)` evaluates the expression, binds the name, **and** produces the value, all
inside a bigger expression. Where could you use it inside `print(...)`?

## Hint 2

Python evaluates function arguments from left to right. So a name bound by `:=` in the first
argument can be used in the second, third and fourth.

## Hint 3

```
print((n := int(input())), (sq := n * n), sq % 7, sq > 100, sep=" | ")
```

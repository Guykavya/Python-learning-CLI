## Approach

Combine the two calculators of the chapter:

- Inside one bracket level, keep a stack of **terms**. Apply the operator that came **before** each number: `+` pushes it, `-` pushes its negative, `*` and `/` combine it with the top term at once (they bind tighter). The level's value is the sum of the terms.
- A `(` starts a new level: evaluate it with a recursive call that stops at the matching `)`, and treat its value like a number that was just read.

Unary minus needs no special code: at the start of a level `op` is `"+"` and `number` is 0, so `-x` is evaluated as `0 - x`. Because division truncates toward zero, `(-a)/b` and `-(a/b)` give the same result, so this is safe for `/` too.

## Code

```python
def trunc_div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def calculate(s):
    s = s.replace(" ", "")

    def parse(i):
        """Evaluate from s[i] up to the matching ')' (or the end). Return (value, index of that ')')."""
        stack = []
        number = 0
        op = "+"
        while True:
            ch = s[i] if i < len(s) else ")"
            if ch.isdigit():
                number = number * 10 + int(ch)
            elif ch == "(":
                number, i = parse(i + 1)          # i is now at the matching ')'
            else:
                if op == "+":
                    stack.append(number)
                elif op == "-":
                    stack.append(-number)
                elif op == "*":
                    stack.append(stack.pop() * number)
                else:
                    stack.append(trunc_div(stack.pop(), number))
                if ch == ")":
                    return sum(stack), i
                op = ch
                number = 0
            i += 1

    value, _ = parse(0)
    return value
```

## Complexity

`O(n)` time: every character is read once, by exactly one level of `parse`. Memory is `O(n)` for the term stacks plus `O(d)` recursion depth for `d` levels of brackets (fine up to the recursion limit of about 1000).

## Another way

Without recursion: two stacks, one for numbers and one for operators, as in shunting-yard, but instead of writing postfix you apply each popped operator to the top two numbers at once. Unary minus is then handled by pushing a `0` when a `-` appears at the start or right after `(`. This version has no depth limit, at the cost of more bookkeeping.

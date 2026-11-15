# Trace: the shunting-yard stacks

This is the chapter's `to_postfix` (section 6), unrolled for the expression `3+4*2/(1-5)` with one `print` after every token. Predict **exactly** what it prints. Do not run it.

```python
PREC = {"+": 1, "-": 1, "*": 2, "/": 2}

tokens = ["3", "+", "4", "*", "2", "/", "(", "1", "-", "5", ")"]
out, ops = [], []
for t in tokens:
    if t.isdigit():
        out.append(t)
    elif t in PREC:
        while ops and ops[-1] in PREC and PREC[ops[-1]] >= PREC[t]:
            out.append(ops.pop())
        ops.append(t)
    elif t == "(":
        ops.append(t)
    else:                                  # ")"
        while ops[-1] != "(":
            out.append(ops.pop())
        ops.pop()                          # discard the "("
    print(t, "| out:", " ".join(out), "| ops:", " ".join(ops))
while ops:
    out.append(ops.pop())
print("end | out:", " ".join(out))
```

Write your answer in `answer.txt`, one printed line per line. Each line has the form

```text
TOKEN | out: OUTPUT | ops: OPERATORS
```

with the items separated by single spaces, the operator stack written **bottom first** (as the list is stored), and nothing after `ops:` when the stack is empty. For example, after the first token the line is `3 | out: 3 | ops:`. The last line starts with `end`.

## How to work

Keep two rows on paper: the output (grows to the right) and the operator stack (top on the right). For an operator, first look at the top of the stack and pop while its precedence is **higher or equal**; only then push the new operator.

## After you answer

1. At the token `/`, why does `*` leave the stack but `+` does not?
2. Why does the `-` inside the brackets not push out the `/` below the `(`?
3. Evaluate the final postfix with integer arithmetic that truncates toward zero. What do you get? (The chapter's `eval_rpn` gives 1.)

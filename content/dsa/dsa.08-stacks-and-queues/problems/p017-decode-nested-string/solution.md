## Approach

Every `[` opens an unfinished piece of text; a `]` finishes the most recent one. That is the stack pattern. At `[` we save the text built so far at the outer level and the repeat count, then start building the inner text from scratch. At `]` the inner text is complete: repeat it and glue it onto the saved outer text.

## Code

```python
def decode(s):
    stack = []                     # (text before the group, repeat count)
    current = ""
    k = 0
    for ch in s:
        if ch.isdigit():
            k = k * 10 + int(ch)
        elif ch == "[":
            stack.append((current, k))
            current, k = "", 0
        elif ch == "]":
            outer, times = stack.pop()
            current = outer + current * times
        else:
            current += ch
    return current
```

## Complexity

Linear in the size of the **output** (plus the input): every character of the result is created by a string repetition or concatenation. Building with `+=` on long strings can copy them several times; for very large outputs, keep lists of pieces and `"".join` them.

## Another way

Recursion (dsa.07): a function `parse(i)` reads letters and groups until it meets `]`, and calls itself for each `k[`. The call stack does the job of the explicit stack:

```python
def decode(s):
    def parse(i):
        out, k = [], 0
        while i < len(s) and s[i] != "]":
            ch = s[i]
            if ch.isdigit():
                k = k * 10 + int(ch)
            elif ch == "[":
                inner, i = parse(i + 1)
                out.append(inner * k)
                k = 0
            else:
                out.append(ch)
            i += 1
        return "".join(out), i
    return parse(0)[0]
```

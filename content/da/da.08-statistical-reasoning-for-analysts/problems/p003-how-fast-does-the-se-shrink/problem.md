# How fast does the SE shrink?

Chapter section 2. The standard error falls like `1 / sqrt(n)`: four times as much data, half the SE.

```python
import math

sd = 20
for n in (25, 100, 400, 1600):
    print(f"n = {n:4d}  SE = {sd / math.sqrt(n):.2f}")
print("to halve the SE, multiply n by", 100 // 25)
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Pay attention to the spaces inside the
formatted numbers (`:4d` pads to 4 characters).

Do not run the code before you have written your answer.

## Example

For `sd = 10` and `n = 4` the line would be `n =    4  SE = 5.00`.

## After you answer

- Which `n` gives SE 0.50 and what did it cost compared with SE 4.00?
- If a survey with n = 400 has a margin you find too wide, what n would halve it?

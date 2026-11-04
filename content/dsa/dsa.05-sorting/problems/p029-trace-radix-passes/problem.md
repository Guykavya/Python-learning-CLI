# Trace radix sort passes

Predict **exactly** what this program prints. Do not run it.

```python
a = [170, 45, 75, 90, 802, 24, 2, 66]
exp = 1
while max(a) // exp > 0:
    buckets = [[] for _ in range(10)]
    for x in a:
        buckets[(x // exp) % 10].append(x)
    a = [x for bucket in buckets for x in bucket]
    print("exp", exp, a)
    exp *= 10
print("done", a)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

In each pass, find the digit `(x // exp) % 10` of every number (ones digit when `exp = 1`, tens when `exp = 10`, hundreds when `exp = 100`).
Put the numbers into buckets `0..9` **in the order they currently appear**, then read the buckets from 0 to 9. Digits that do not exist (for example the tens digit of 2) are 0.
The loop stops when `max(a) // exp` is 0: here the largest number is 802.

## After you answer

1. How many passes ran, and why that many?
2. In the second pass, `802` and `2` share the tens digit 0. In which order do they appear, and why is that the order that makes the final result correct?
3. What would go wrong if the buckets were filled from the end of the list instead of the start?

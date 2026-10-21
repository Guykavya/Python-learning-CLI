# Trace loop else clauses

Predict **exactly** what this program prints. Do not run it. Think carefully about when
each `else` block runs.

```python
for word in ["sky", "tree", "", "moon"]:
    for ch in word:
        if ch in "aeiou":
            print(word, "has vowel", ch)
            break
    else:
        print(repr(word), "no vowel")

count = 0
while count < 3:
    count += 1
    if count == 5:
        break
else:
    print("while finished, count =", count)

for i in range(3):
    if i == 1:
        continue
    print("i =", i)
else:
    print("for finished, i =", i)

n = 10
while n > 0:
    n -= 4
    if n < 0:
        print("went negative:", n)
        break
else:
    print("never negative")
print("end", n)
```

Write your answer in `answer.txt`, one printed line per line.

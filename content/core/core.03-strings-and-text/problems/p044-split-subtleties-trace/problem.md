# split() subtleties

Predict **exactly** what this program prints, one line per `print`. Do not run it until you have written your answer.

```python
print("a  b".split(" "))
print("a  b".split())
print("  x ".split())
print("".split())
print("".split(","))
print("a,b,,c,".split(","))
print("1-2-3-4".split("-", 2))
print("1-2-3-4".rsplit("-", 1))
print("x\ny\n".split("\n"))
print("x\r\ny\n".splitlines())
print(len("one two  three".split(" ")))
print("-".join("a b  c".split()))
```

Write your answer in `answer.txt`, one line per printed line.

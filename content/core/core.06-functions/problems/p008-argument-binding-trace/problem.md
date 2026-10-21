# Who gets which value?

Predict **exactly** what this program prints. Use the binding steps from the chapter:
positionals first, then keywords, then defaults for the empty slots.

```python
def order(a, b=2, c=3):
    print("a =", a, "b =", b, "c =", c)

def tag(text, left="[", right="]", sep=""):
    return left + sep + text + sep + right

order(1)
order(1, 5)
order(1, c=9)
order(c=1, a=2)
order(7, 8, 9)
print(tag("hi"))
print(tag("hi", "<", ">"))
print(tag("hi", sep=" "))
print(tag("hi", right="}", left="{"))
print(tag(sep="-", text="x", left="(", right=")"))
```

Write your answer in `answer.txt`, one line per printed line.

# A wrong type still runs: what prints?

Python ignores type hints when it runs the program. Here is a program with hints and several calls
that break them. Predict **exactly** what it prints when you run it with `python`.

```python
def double(n: int) -> int:
    return n * 2


def shout(text: str) -> str:
    return text.upper()


print(double(4))
print(double("ab"))
print(double([1, 2]))
print(double(2.5))
print(shout("hey"))
try:
    print(shout(5))
except AttributeError:
    print("AttributeError")
print(double.__annotations__ == {"n": int, "return": int})
```

Write the lines the program prints, one per line, in order.

Write your answer in `answer.txt`.

(Lists print with brackets and a space after each comma, for example `[1, 2, 1, 2]`.)

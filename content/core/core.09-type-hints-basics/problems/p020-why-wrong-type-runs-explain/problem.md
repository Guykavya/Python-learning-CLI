# Explain: why does a wrongly typed call still run?

Dev writes this and is surprised:

```python
def area(width: float, height: float) -> float:
    return width * height


print(area("3", 4))      # prints 3333, no error
```

"I wrote `float`! Why did Python not stop me, and why is the answer `3333`?"

In `answer.md` (about 120 to 250 words), explain:

1. Why does the call run at all? What does the Python interpreter do with the hints
   `width: float`?
2. Why is the result `3333`, and why is that more dangerous than a crash?
3. Which tool would reject the call, and **when** does it do it? Does that tool run the program?
   Use the words **static** and **runtime**.
4. Dev now wants the function itself to refuse a string, even when mypy is not used. What must he
   add, and where does that kind of check belong in a program?

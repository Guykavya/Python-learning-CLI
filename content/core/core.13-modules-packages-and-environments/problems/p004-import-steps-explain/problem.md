# Explain: what `import` does, and why the `__main__` guard exists

Ravi wrote a small module with a demo at the bottom:

```python
# temps.py
def c_to_f(c):
    return c * 9 / 5 + 32

print("Demo:", c_to_f(100))
```

and a program that uses it:

```python
# report.py
import temps
import temps
print(temps.c_to_f(37))
```

Running `python report.py` prints:

```text
Demo: 212.0
98.6
```

Ravi asks: "Why does my demo line appear at all? I only wanted the function. And why does it appear
**once**, when I wrote `import temps` twice?"

In `answer.md` (about 200 to 350 words), explain:

1. Step by step, what Python does the **first** time it runs `import temps`: where it looks for the
   file, what object it creates, where it stores that object, which code runs, and which name it binds.
2. What Python does the **second** time it runs `import temps`, and why the demo is not printed again.
3. What `__name__` is inside `temps.py` when it is imported, and what it is when you run
   `python temps.py`.
4. How to change `temps.py` so the demo runs only with `python temps.py`. Show the code.
5. One other reason the guard matters (think of tests that import the module, or a slow job at the bottom of a file).

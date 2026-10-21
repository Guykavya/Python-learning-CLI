# Why `is` sometimes seems to work

A classmate typed this into the Python REPL (the `>>>` prompt), one line at a time:

```python
>>> a = 256
>>> b = 256
>>> a is b
True
>>> a = 257
>>> b = 257
>>> a is b
False
>>> a == b
True
```

They conclude: "`is` works for numbers up to 256, so I can use it to compare small numbers."
Also, when they type `x is 5`, Python prints `SyntaxWarning: "is" with 'int' literal. Did you mean "=="?`

Explain in `answer.md`:

1. The difference between `is` and `==`.
2. Why `256` gave `True` but `257` gave `False` in this REPL session.
3. Why the classmate's conclusion is wrong (give at least two reasons).
4. Why Python warns about `x is 5`.
5. When you **should** use `is`.

# Make the failing tests pass: count_vowels

The tests in `test_solution.py` describe `count_vowels(text)`. Read them first: they are the
whole specification. Then write the function in `solution.py` until every test passes.

From the tests you can read off the rules:

- count the letters `a e i o u`
- upper-case vowels count too
- `y` is **not** a vowel
- an empty string has 0 vowels

**Examples**

```python
count_vowels("hello")    # 2
count_vowels("AEIOU")    # 5
count_vowels("rhythm")   # 0
count_vowels("")         # 0
```

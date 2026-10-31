# re.sub with a function: double every integer

A recipe for 2 people must serve 4, so every quantity doubles. A replacement **string** cannot
compute anything, but `re.sub` also accepts a **function**: it is called with each Match object
and returns the text to put in its place.

Write `double_numbers(s: str) -> str` in `solution.py` that replaces every integer in `s` by
twice its value.

What counts as an integer:

- A run of digits that does not touch a letter, digit or `_` on either side. So `mp3`, `3rd`
  and `a1b` are left alone.
- Not part of a decimal number: `2.5` is left alone. A full stop that ends a sentence is fine:
  `buy 7.` becomes `buy 14.`
- A `-` in front just stays where it is: `-4 apples` becomes `-8 apples`, and `5-3` becomes
  `10-6`. (Think about why you do not need to treat the minus sign specially when *doubling*.)
- Leading zeros are dropped by the doubling: `007` becomes `14`.

Everything else in the string stays exactly as it was.

**Example**

```python
double_numbers("2 eggs, 150 g flour, 1 cup milk")  # '4 eggs, 300 g flour, 2 cup milk'
double_numbers("Cool to -4 degrees")               # 'Cool to -8 degrees'
double_numbers("5-3 and mp3 at 2.5x")              # '10-6 and mp3 at 2.5x'
```

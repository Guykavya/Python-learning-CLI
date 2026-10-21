# Make the failing tests pass: parse_time

`parse_time("1:30")` turns a time such as `"H:MM"` into a number of minutes. The tests are the
specification: read them, then write the function. In words:

- the text has **exactly two parts** around one colon: hours and minutes;
- hours can be any whole number from 0 up; minutes must be two digits, 00 to 59;
- the result is `hours * 60 + minutes`;
- a text without exactly one colon raises `ValueError` with a message containing `"H:MM"`;
- hours or minutes that are not whole numbers raise `ValueError` with a message containing
  `"whole numbers"`;
- minutes above 59 raise `ValueError` with a message containing `"minutes"`;
- surrounding spaces in the text are ignored.

**Examples**

```python
parse_time("1:30")      # 90
parse_time("0:05")      # 5
parse_time(" 12:00 ")   # 720
parse_time("1:60")      # raises ValueError (minutes ...)
parse_time("130")       # raises ValueError (expected H:MM)
```

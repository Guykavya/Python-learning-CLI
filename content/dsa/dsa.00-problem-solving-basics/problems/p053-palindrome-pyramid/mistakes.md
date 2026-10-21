- Starting the falling part at `i` instead of `i - 1`. The peak is then written twice: `123321`
  instead of `12321`.
- Writing the full number instead of its last digit. Row 10 becomes `123456789109...` and the
  triangle loses its shape, because `10` takes two characters.
- Printing digits one at a time with `print(x, end=" ")`. That puts a space between the digits
  (and often a trailing space), which does not match the required output.
- Using `n - i + 1` spaces, which shifts every row one place right, so the last row starts with a
  space.

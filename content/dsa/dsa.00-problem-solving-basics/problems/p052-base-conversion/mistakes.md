- Appending each digit at the end (`result = result + digit`). The remainders come out last digit
  first, so 13 in base 2 prints `1011` instead of `1101`.
- Forgetting `n == 0`. The `while m > 0` loop never runs and the program prints an empty line.
- Working on the negative number directly. `-10 % 3` is `2` and `-10 // 3` is `-4` in Python, so
  `m` never reaches 0 with `while m > 0` (the loop is skipped), or loops wrongly with `m != 0`.
- Checking the base after the loop, or not at all. With `b = 1`, `m // 1` never shrinks and the
  program runs forever; with `b = 17` there is no digit symbol for 16.

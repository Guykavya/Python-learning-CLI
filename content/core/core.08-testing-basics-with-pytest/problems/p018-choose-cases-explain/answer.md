**1. Cases, one per path (and a few borders).**

| year | expected | why it is different |
|---|---|---|
| 2000 | True | divisible by 400: the first branch (exception to the exception) |
| 1900 | False | divisible by 100 but not by 400: the second branch |
| 2024 | True | divisible by 4, not by 100: the last line, true case |
| 2023 | False | divisible by nothing: the last line, false case |
| 2100 | False | another century that is not a leap year, in case a program special-cases 1900 only |
| 2400 | True | another multiple of 400 |
| 4 | True | the smallest ordinary leap year; guards against `year > 4` slips |
| 2025 | False | the year right after a leap year: catches `% 4 <= 1` style slips |

Each row catches a different plausible bug: forgetting the 400 rule (2000 would give False),
forgetting the 100 rule (1900 would give True), forgetting the 4 rule (2023 would give True or
2024 False).

**2. Why eight leap years are a poor suite.** 1996, 2004, 2008, 2012, 2016, 2020 and 2024 are all
divisible by 4 and not by 100: they all take the same path. They are **redundant**: if one passes
the others almost surely pass. The suite looks big but never tests the two exceptions; 2000 is
there only by luck and no non-leap year at all is tried, so a function that always returns True
passes six of the eight. Eight tests, three kinds of bug uncaught.

**3. Boundaries.** 1900/2000 and 2100/2400 are the borders of the century rules: they catch a
function that treats every multiple of 100 the same way (all leap or all not). 1999/2001 around
2000, and 2023/2025 around 2024, catch an off-by-one in the modulo. Years such as 4 or 0 are the
smallest values where an `if year > 0` or similar guard could go wrong.

**4. Negative and text input.** First decide the contract: does the docstring say years are
positive whole numbers? If so, `-4` and `"2024"` are invalid input, and the right test is that
they raise `ValueError` or `TypeError` (and the function must be changed to do so: today `"2024" % 400`
raises `TypeError` by accident). If the function should be defined for negative years too, then
-4 is a normal test. I would not test behaviour that nobody decided on: that locks in an accident.

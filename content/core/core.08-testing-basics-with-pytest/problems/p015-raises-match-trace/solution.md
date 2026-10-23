## Walkthrough

- `test_a`: `"abc"` is not digits, `ValueError` raised: PASSED.
- `test_b`: the message `age must be digits, got 'abc'` contains `digits`: PASSED.
- `test_c`: the message does not contain `large`: FAILED (the `ValueError` is raised but the message does not match).
- `test_d`: the exception is a `ValueError`, not a `TypeError`, so it escapes: FAILED.
- `test_e`: `parse_age("42")` returns 42 and raises nothing: FAILED with DID NOT RAISE.
- `test_f`: `"200"` is digits but above 150; message `age too large: 200` matches: PASSED.
- `test_g`: `None.isdigit()` raises `AttributeError`, which is an `Exception`: PASSED. A test this loose cannot tell a bug from the behaviour you wanted.
- `test_h`: `info.value` is the exception; its text contains `'x'`: PASSED.
- `test_i`: as a regular expression `a+b` means "one or more a followed by b". The message is `age must be digits, got 'a+b'`: there is no `ab` in it, so FAILED. Use `match=re.escape("a+b")` or a plain word.

## The exact output

```text
test_a PASSED
test_b PASSED
test_c FAILED
test_d FAILED
test_e FAILED
test_f PASSED
test_g PASSED
test_h PASSED
test_i FAILED
4 failed, 5 passed
```

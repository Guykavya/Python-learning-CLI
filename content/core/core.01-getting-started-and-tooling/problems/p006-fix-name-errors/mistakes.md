- Defining a new variable `semster = 1` to silence the error. The bug is the
  typo; now you have two names for the same thing.
- Replacing the variable with text, `print("College:", "City College")`. It hides
  the bug instead of fixing it, and breaks when the variable changes.
- Expecting all three errors at once. Python stops at the first runtime error, so
  you will see them one by one. "Course: BCA" prints only after bug 1 is fixed.

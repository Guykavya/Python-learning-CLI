# Explain: which cases are worth testing?

You have to test this function, which says whether a year is a leap year (divisible by 4, except
years divisible by 100, unless also divisible by 400):

```python
def is_leap_year(year):
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0
```

In `answer.md`:

1. List **at least six** specific years you would test, each with its expected result and a few
   words on **why this case is different** from the others. Your list must not contain two cases
   that exercise exactly the same path.
2. A classmate proposes testing 1996, 2000, 2004, 2008, 2012, 2016, 2020 and 2024. Explain why
   eight tests may still be a poor suite. Use the word **redundant**.
3. Which years sit on the **boundaries** of the rule, and what kind of bug would each catch?
4. Should you also test `is_leap_year(-4)` or `is_leap_year("2024")`? Say what you would decide
   and what you would need to know first.

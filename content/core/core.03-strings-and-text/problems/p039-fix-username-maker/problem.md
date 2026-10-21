# Fix the username maker

A classmate wrote a program that makes usernames for a college portal. It has several bugs. **Fix** `starter.py` (copy it into `solution.py` first) so that it follows this specification.

**Specification.** Read two lines:

1. a full name: at least two words, possibly with extra spaces at the ends **and between words**, in any mix of case;
2. a birth year: four digits, possibly with spaces around it.

Print three lines:

```
Hello, <the name with single spaces, each word in title case>!
Username: <first word lowercase><first letter of the LAST word lowercase><last two digits of the year>
Age in 2026: <2026 minus the birth year>
```

**Example**

Input:
```
  asha   rani KUMAR
 2005
```
Output:
```
Hello, Asha Rani Kumar!
Username: ashak05
Age in 2026: 21
```

There are at least five bugs. Some crash, some quietly give wrong output. The tests explain what each one causes.

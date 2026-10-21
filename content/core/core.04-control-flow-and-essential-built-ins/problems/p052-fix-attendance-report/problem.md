# Fix the attendance report

A classmate wrote an attendance report. It runs without crashing on their test, but the
results are wrong. **Fix** `starter.py` (copy it into `solution.py` first) so that it follows
the specification.

**Specification.** The first line holds the student names, separated by spaces. Then comes
one line per student, in the same order, made of `P` (present) and `A` (absent) marks, one
per day. Marks may be small letters too (`p`, `a`). Every line has at least one mark.

For each student print:

```
<n>. <name>: <present>/<days> (<percent>%)
```

where `n` counts from 1 and the percent is shown with no decimals (`:.0f`). Add ` LOW` at the
end of the line if the percent is **below** 75.

After all students, print `All students at 75% or above` if nobody was low, otherwise
`Low attendance: <how many>`.

**Example**

Input:
```
Asha Ravi Meena
PPPA
PAAA
pppp
```
Output:
```
1. Asha: 3/4 (75%)
2. Ravi: 1/4 (25%) LOW
3. Meena: 4/4 (100%)
Low attendance: 1
```

There are five bugs. The tests describe the symptom each one causes.

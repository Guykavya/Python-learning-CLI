# Report card table

Read a line of subjects and a line of marks (whole numbers), both separated by spaces.

If the counts differ, print only `Mismatch`. Otherwise print a table:

```
No  Subject     Marks  Result
1   Maths          91  PASS
2   Physics        38  FAIL
```

- `No` is left-aligned in 4 characters, the subject left-aligned in 12, the marks
  right-aligned in 5, then two spaces and `PASS` (40 or more) or `FAIL`.
- The header uses the same widths: `f"{'No':<4}{'Subject':<12}{'Marks':>5}  Result"`.

Then print `Passed P of N` and `Overall: PASS` if every subject passed, otherwise
`Overall: FAIL`. With no subjects at all, print only the header and `Passed 0 of 0` and
`Overall: PASS`.

## Hint 1

For every line, first find the separators (the matches) in the text, then write the pieces
between them. Only then ask: does the pattern have a capturing group? If so, insert each match's
group values between the pieces.

## Hint 2

Line 3 puts the spaces **inside** the group, line 2 does not: compare what is kept. Line 6 has
two groups, so every match adds **two** items, one of them `None`.

```
"1-2+3" with (-)|(\+):
   match "-" : group1 "-", group2 None
   match "+" : group1 None, group2 "+"
-> pieces 1, 2, 3 with [g1, g2] between them
```

## Hint 1

How do you get at the text a function printed? Call the function, then
`out = capsys.readouterr().out`. What type is `out`, and which string method turns it into a
list of lines?

## Hint 2

Think about which **order** and **format** details a buggy version could get wrong: sorted by
name (use names whose alphabetical order differs from both the input order and the amount
order), two decimals (use `4.5` and a whole number), the total line, the empty list, and which
stream (`.out` or `.err`) the text lands on.

```
print_report([("tea",1.0),("cake",9.0),("apple",5.0)])
lines = capsys.readouterr().out.splitlines()
assert lines == ["apple: 5.00", "cake: 9.00", "tea: 1.00", "TOTAL: 15.00"]
assert capsys.readouterr().err == ""
```

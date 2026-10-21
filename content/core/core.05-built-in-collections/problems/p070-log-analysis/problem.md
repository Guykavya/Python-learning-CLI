# Analyse a web log

A web server log has one line per visit: `day user page` (day is an integer). Read `n`, then
`n` lines. Print:

```
Events: <n>
Distinct users: <number of different users>
Top pages:
  <page> <visits>
  ... (up to 3 pages, most visits first, ties by page name)
Loyal users: <users who appear on EVERY day that occurs in the log, sorted, or none>
Busiest day: <day> (<visits>)
```

For the busiest day, break ties with the **smaller** day number. If `n` is 0, print only
`Events: 0`.

**Example**

Input:
```
6
1 asha home
1 ravi cart
2 asha home
2 meena home
3 asha about
3 ravi home
```
Output:
```
Events: 6
Distinct users: 3
Top pages:
  home 4
  about 1
  cart 1
Loyal users: asha
Busiest day: 1 (2)
```

The tests use 200,000 lines. Choose structures so that every step is close to O(n).

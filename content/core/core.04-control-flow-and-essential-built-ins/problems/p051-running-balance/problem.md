# Running balance with early exit

The first line is the opening balance (a whole number of rupees). Then come transactions,
one per line, until a line `end`:

- `+N` deposits N rupees, `-N` withdraws N rupees (N is a whole number, digits only).
- After each valid transaction, print `#K OK, balance B`, where K counts valid transactions
  from 1.
- A line that is not `+` or `-` followed by digits: print `Skipped: <line, stripped>`. It does
  not count as a transaction.
- If a withdrawal is larger than the balance, print
  `#K declined: balance B, needed N` and **stop processing**: do not read any more lines.

At the end (after `end`, or after a decline) print `Final balance: B`.

**Example**

Input:
```
1000
+500
-200
oops
-2000
+50
```
Output:
```
#1 OK, balance 1500
#2 OK, balance 1300
Skipped: oops
#3 declined: balance 1300, needed 2000
Final balance: 1300
```

The `+50` line is never read.

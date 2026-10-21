# Count the votes

Read `n`, then `n` votes, one candidate name per line. Print every candidate with their votes,
most votes first, ties in alphabetical order:

```
<name>: <votes>
```

Then print the result:

- `Winner: <name>` if one candidate has the most votes, or
- `Tie: <name>, <name>, ...` (alphabetical, joined by `, `) if several share the most.

If `n` is 0, print only `No votes`.

**Example**

Input:
```
5
ravi
asha
ravi
asha
meena
```
Output:
```
asha: 2
ravi: 2
meena: 1
Tie: asha, ravi
```

## Walkthrough: pwwkew

| r | s[r] | drops | l after | window | best |
|---|---|---|---|---|---|
| 0 | p | | 0 | p | 1 |
| 1 | w | | 0 | pw | 2 |
| 2 | w | p, w | 2 | w | 2 |
| 3 | k | | 2 | wk | 2 |
| 4 | e | | 2 | wke | 3 |
| 5 | w | w | 3 | kew | 3 |

At `r = 2` the second `w` is in `seen`. Dropping `p` is not enough (`w` is still inside), so the loop drops `w` too.
At `r = 5` only the `w` at position 2 has to leave; `k` and `e` stay.

## dvdf and abba

`dvdf`: at `r = 2` the window is `dv`. Only the first `d` leaves; `l` becomes 1 and the window is `vd`. Then `f`
makes `vdf`, length 3. Restarting at the repeat would give `df`, length 2: wrong.

`abba`: at `r = 2`, `a` and then `b` are dropped (`l = 2`). At `r = 3` the set is `{b}`, so the `a` enters with no
drop. The window is `ba`, length 2, and `best` stays 2.

## Output

```
0 p 0 p 1
1 w 0 pw 2
drop p
drop w
2 w 2 w 2
3 k 2 wk 2
4 e 2 wke 3
drop w
5 w 3 kew 3
answer 3
0 d 0 d 1
1 v 0 dv 2
drop d
2 d 1 vd 2
3 f 1 vdf 3
answer 3
0 a 0 a 1
1 b 0 ab 2
drop a
drop b
2 b 2 b 2
3 a 2 ba 2
answer 2
```

## Key ideas

- Every character is added once and dropped at most once: `pwwkew` has 6 additions and 3 drops. That is why the
  `while` inside the `for` is still O(n) in total.
- The window only ever loses characters from the left, and only as many as needed to remove the old copy.
- `best` is a running maximum; the window itself can get shorter.

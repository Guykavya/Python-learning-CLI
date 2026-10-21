# Roman numerals to numbers

Roman numerals use `I`=1, `V`=5, `X`=10, `L`=50, `C`=100, `D`=500, `M`=1000. Normally the
values are added, largest first: `XVI` = 10 + 5 + 1 = 16. But when a smaller value comes
**directly before** a larger one, it is **subtracted**: `IV` = 4, `XC` = 90, `MCMXCIV` =
1000 + (1000 - 100) + (100 - 10) + (5 - 1) = 1994.

The first line is a number `N`, then `N` lines, each a numeral (strip spaces, accept small
letters). Print `<NUMERAL> = <value>` with the numeral in capitals. If a line is empty or
contains any other character, print `<line> is not a Roman numeral`.

You do not need to reject badly formed numerals such as `IIII` or `VX`; just apply the rule
above (`IIII` gives 4, `VX` gives 5).

**Example**

Input:
```
3
xiv
MCMXCIV
12
```
Output:
```
XIV = 14
MCMXCIV = 1994
12 is not a Roman numeral
```

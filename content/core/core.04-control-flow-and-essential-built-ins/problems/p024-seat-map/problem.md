# Cinema seat map

Read three lines:

1. the number of rows (1 to 99)
2. the seat letters of one row, where a **space** marks the aisle, for example `AB CD`
3. the booked seats, separated by spaces, for example `1A 2D 3B` (the line may be empty)

Print one line per row: `Row N: ` followed by the row's seats, where a booked seat shows
`X`, a free seat shows its letter, and the aisle shows a space. Write `N` right-aligned in
2 characters. Finally print `Free: F of T`.

Booked seats that do not exist (like `9Z` in a 3-row hall) are ignored.

**Example**

Input:
```
3
AB CD
1A 2D 3B 9Z
```
Output:
```
Row  1: XB CD
Row  2: AB CX
Row  3: AX CD
Free: 9 of 12
```

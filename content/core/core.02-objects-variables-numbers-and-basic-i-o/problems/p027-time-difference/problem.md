# Minutes between two clock times

Read four whole numbers, each on its own line: start hour, start minute, end hour, end minute
(24-hour clock). The end time is always the **next** time the clock shows those numbers, so if
it is earlier than the start, the period crosses midnight. If both times are equal, the duration is 0.

Print:

```
<hours> h <minutes> min
```

**Example**

Input:
```
22
30
6
0
```
Output:
```
7 h 30 min
```

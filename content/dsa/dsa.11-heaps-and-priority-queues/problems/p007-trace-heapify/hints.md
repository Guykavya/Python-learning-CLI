## Hint 1

`n = 7`, so the loop runs for `i = 2, 1, 0` (`n // 2 - 1 = 2`). Indexes 3 to 6 are leaves and are never sifted. The first line is `sift_down from index 2 (value 7)`. The children of index 2 are index 5 (`2`) and index 6 (`8`). The smaller one is `2`, and `2 < 7`, so there is one `swap` line: `swap a[2]=7 with a[5]=2`. Then the item 7 sits at index 5, a leaf, and the call ends. After the call, the printed list is `[9, 4, 2, 1, 6, 7, 8]`.

## Hint 2

Index 1 holds `4`, with the children `1` (index 3) and `6` (index 4). Index 0 holds `9`; at that time its children are `1` (index 1, changed by the previous step) and `2` (index 2, changed by the first step). Always read the values from the **current** list, not from the starting list. After the first swap at index 0, the item 9 stands at index 1, and its children are the items at indexes 3 and 4.

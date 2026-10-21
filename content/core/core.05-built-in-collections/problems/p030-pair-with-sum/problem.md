# Find a pair with a given sum

Read a line of integers and then a target integer. Find two **different positions** `i < j`
whose numbers add up to the target. Choose the pair with the **smallest `j`**; for that `j`,
use the **smallest `i`**. Print (positions start at 1):

```
<i> <j>
```

or `No pair` if none exists.

**Example**

Input:
```
8 3 5 3 7
10
```
Output:
```
2 5
```

Position 5 (value 7) is the first place where an earlier number completes the sum: 3 at
position 2. Note that `5 + 5` would also be 10, but there is only one 5.

The tests include 100,000 numbers, so checking every pair (O(n²)) is far too slow.

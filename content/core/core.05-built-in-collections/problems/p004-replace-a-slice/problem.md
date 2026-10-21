# Replace a slice

Read three lines:

1. a list of integers separated by spaces
2. two integers `i j`
3. replacement integers separated by spaces (this line may be empty)

Do **one** slice assignment, `nums[i:j] = replacement`, then print the list with spaces
between numbers. If the list ends up empty, print `(empty)`.

Remember that the replacement can be shorter or longer than the slice, so the list can shrink
or grow. An empty replacement deletes the slice. When `i == j`, nothing is removed and the new
numbers are inserted.

**Example**

Input:
```
10 20 30 40 50
1 3
7 8 9
```
Output:
```
10 7 8 9 40 50
```

`nums[1:3]` is `[20, 30]`. It is replaced by `[7, 8, 9]`.

# Remove every copy

Read a line of words, then a target word on the next line. Remove **every** copy of the
target and print:

```
<remaining words separated by spaces>
Removed: <how many were removed>
```

If no words remain, print `(empty)` on the first line instead.

**Example**

Input:
```
to be or not to be
to
```
Output:
```
be or not be
Removed: 2
```

Be careful: `list.remove(x)` removes only the **first** copy. And removing items from a list
while a `for` loop walks over that same list skips items.

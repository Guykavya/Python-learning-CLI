# Longest run of consecutive numbers

Read a line of integers (any order, repeats allowed, may be empty). Find the longest run of
**consecutive integer values** that all appear in the list, such as `4 5 6 7`. Print:

```
Length: <length of the longest run>
Run: <first> to <last>
```

If several runs are equally long, report the one with the **smallest** first value. For an
empty line print only `Length: 0`.

**Example**

Input:
```
100 4 200 1 3 2 101 4
```
Output:
```
Length: 4
Run: 1 to 4
```

The tests include 200,000 numbers. Aim for O(n) with a set (sorting first, O(n log n), is also
fast enough; checking `x + 1 in a_list` is not).

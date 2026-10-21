# Filter and transform

Read one line of integers (it may be empty). Print three lines, each built with a
comprehension:

1. the **squares of the even numbers**, as a list
2. every number, but with negatives replaced by `0`, as a list
3. the distinct remainders when the numbers are divided by 3, **sorted**, as a list

Print the lists exactly as Python shows them.

**Example**

Input:
```
4 -3 7 -8 0 5
```
Output:
```
[16, 64, 0]
[4, 0, 7, 0, 0, 5]
[0, 1, 2]
```

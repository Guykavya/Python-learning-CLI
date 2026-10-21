# Explain two off-by-one bugs

Each program below was written to do the job in its title. Both look reasonable. Both are wrong.

**Program A: sum all integers from `a` to `b` inclusive**

```python
a = int(input())
b = int(input())
total = 0
for i in range(a, b):
    total += i
print(total)
```

**Program B: count the digits of `n` (where `n >= 0`)**

```python
n = int(input())
count = 0
while n > 10:
    n //= 10
    count += 1
print(count)
```

For example, Program A should print 15 for `a = 1`, `b = 5`, and Program B should print 3 for `n = 472`
and 1 for `n = 0`.

In `answer.md`, answer these questions. Do the dry runs **on paper first**, then you may run the code to check.

1. For each program, find the bug with a **dry run** on a small input. Show a trace table
   (one row per loop pass, one column per variable).
2. Explain why each bug is called an "off-by-one" error. Program B has **more than one** problem. Find all of them,
   and say for which inputs each one shows up.
3. Give the fixed code for each program, and check your fix on `n = 0` for Program B.
4. Name the specific inputs that would have exposed each bug quickly (think about boundaries such as
   `a == b`, `n = 0`, `n = 9`, `n = 10`, `n = 100`). Then describe the general testing habit that catches this
   kind of bug.

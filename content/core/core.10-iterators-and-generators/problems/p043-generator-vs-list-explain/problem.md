# Explain: a generator or a list?

Run this program (the two big numbers come from one 64-bit Linux machine with Python 3.14; yours
may be a little different):

```python
import sys

squares_list = [n * n for n in range(1_000_000)]
squares_gen = (n * n for n in range(1_000_000))

print(sys.getsizeof(squares_list))
print(sys.getsizeof(squares_gen))
print(sum(squares_list) == sum(squares_gen))
print(sum(squares_gen))
print(len(squares_list))
print(squares_list[10])
```

Output:

```text
8448728
208
True
0
1000000
100
```

`sys.getsizeof(x)` gives the size in bytes of the object `x` itself (for a list, the list's own
table of references, not the numbers inside it).

In `answer.md` (about 150 to 300 words), explain:

1. Why is the list about 8 MB while the generator is about 200 bytes? Would the generator be bigger
   for `range(1_000_000_000)`? Why does `getsizeof` even **under-count** the list's real memory?
2. Why does `sum(squares_gen)` give `0` on the fourth line, right after the comparison was `True`?
3. Name three things a list can do that a generator cannot (lines 5 and 6 show two of them).
4. Give a clear rule: when do you choose a generator, and when a list? Give one example of each from
   real programs (for example, reading a huge log stream, or a menu you show many times).

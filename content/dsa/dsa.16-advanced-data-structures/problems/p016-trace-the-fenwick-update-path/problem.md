# Trace the Fenwick update path

The two loops of a Fenwick tree (chapter section 10), on **1-indexed** positions with `n = 16`: an update climbs by adding the lowest set bit, a prefix query descends by removing it. Each visited cell is printed with its binary form. Predict **exactly** what this program prints. Do not run it.

```python
n = 16

def update_path(k):
    path = []
    while k <= n:
        path.append(k)
        k += k & -k
    return path

def prefix_path(r):
    path = []
    while r > 0:
        path.append(r)
        r -= r & -r
    return path

for k in (11, 6):
    print("update", k, ":", " ".join(f"{p}({p:b})" for p in update_path(k)))
for r in (15, 10):
    print("prefix", r, ":", " ".join(f"{p}({p:b})" for p in prefix_path(r)))
print("cells holding position 6:", sum(1 for k in range(1, n + 1) if k - (k & -k) < 6 <= k))
```

Write your answer in `answer.txt`, one printed line per line.

## How to work

1. Write each starting number in binary. `k & -k` is the value of its lowest `1` bit.
2. For an update: add that bit, write the new number in binary, repeat while the number is `<= 16`.
3. For a prefix: remove that bit, repeat while the number is `> 0`.
4. For the last line, a cell `k` holds the positions `k - lowbit(k) + 1 .. k`. Count the cells that contain position 6.

## After you answer

1. Why does every update path end at 16 here, and why can a path never be longer than 5 cells for `n = 16`?
2. The prefix path of 15 has four cells. Which positions does each of them cover? Do they tile `1..15` without overlap?
3. Compare the last line with the update path of 6. What do you notice?

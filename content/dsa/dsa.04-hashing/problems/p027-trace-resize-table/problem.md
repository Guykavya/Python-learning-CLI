# Trace a table that resizes

This hash table uses chaining, starts with **4 buckets**, and uses `key % size` as the bucket. After every insert, if
`count / size > 0.75` it **doubles** the size and **rehashes**: it visits the old buckets from bucket 0 upward, each chain from
left to right, and appends every key to its bucket in the new table.

Predict **exactly** what the program prints. Do not run it.

```python
size = 4
table = [[] for _ in range(size)]
count = 0


def show():
    print(size, count, table)


def put(key):
    global size, table, count
    table[key % size].append(key)
    count += 1
    if count / size > 0.75:
        old = [k for chain in table for k in chain]
        size *= 2
        table = [[] for _ in range(size)]
        for k in old:
            table[k % size].append(k)
        print("resize to", size)
    show()


for key in [8, 5, 12, 3, 9, 20, 7]:
    put(key)
```

Write your answer in `answer.txt`, one line per printed line. Each `show` line prints `size count table`.

## How to work

Keep the table as a row of lists. After each `put`, compute `count / size`. When it is above 0.75, build the new, larger
table by re-inserting the keys in the order described, and print `resize to ...` **before** the `show` line.

## After you answer

1. Why do keys that collided in the small table often end up in different buckets after the resize?
2. Why does the code rehash every key instead of copying the chains?
3. At which counts does the table resize if you keep inserting new keys (sizes 4, 8, 16)?

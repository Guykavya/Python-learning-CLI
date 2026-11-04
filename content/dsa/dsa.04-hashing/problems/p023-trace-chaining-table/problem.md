# Trace a table with chaining

A tiny hash table has **4 buckets**; each bucket is a list (a **chain**). The "hash" of an integer key is `key % 4`.
Predict **exactly** what the program prints. Do not run it.

```python
M = 4
buckets = [[] for _ in range(M)]


def put(key):
    i = key % M
    if key in buckets[i]:
        print("put", key, "bucket", i, "already there")
    else:
        buckets[i].append(key)
        print("put", key, "bucket", i, "chain length", len(buckets[i]))


def find(key):
    i = key % M
    steps = 0
    for k in buckets[i]:
        steps += 1
        if k == key:
            print("find", key, "found after", steps, "steps")
            return
    print("find", key, "missing after", steps, "steps")


for key in [5, 9, 12, 13, 5, 7, 16, 1, 20]:
    put(key)
print(buckets)
find(13)
find(100)
find(7)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Draw four boxes numbered 0 to 3. For each key compute `key % 4`, then append to the chain unless the key is already
there. `find` walks the chain from the left and counts the steps (comparisons) until it finds the key or runs out.

## After you answer

1. Which keys collide? What do they have in common?
2. Why is searching for `100` fast here but searching for `13` slower?
3. What would happen to the chain lengths if all keys were multiples of 4?

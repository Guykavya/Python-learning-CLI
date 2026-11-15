# Trace linear probing

An **open addressing** table keeps every key directly in a slot of one array. When the home slot `key % 7` is taken, it
tries the next slot (`+1`, wrapping around at the end) until it finds an empty one. This is **linear probing**.
Predict **exactly** what the program prints. Do not run it.

```python
M = 7
slots = [None] * M


def put(key):
    i = key % M
    probes = [i]
    while slots[i] is not None:
        i = (i + 1) % M
        probes.append(i)
    slots[i] = key
    print("put", key, "probes", probes)


def find(key):
    i = key % M
    probes = [i]
    while slots[i] is not None:
        if slots[i] == key:
            print("find", key, "found", probes)
            return
        i = (i + 1) % M
        probes.append(i)
    print("find", key, "missing", probes)


for key in [10, 17, 3, 24, 8, 15]:
    put(key)
print(slots)
find(3)
find(1)
find(31)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Draw 7 empty slots numbered 0 to 6. For each key list the slots tried (the `probes` list), place the key in the first empty
one. A search follows the same probe sequence and stops at the key or at the first **empty** slot.

## After you answer

1. Which keys had to move away from their home slot? What did they collide with?
2. Why can a search stop at the first empty slot and say "missing"?
3. What goes wrong if you simply set a slot back to `None` to delete a key in the middle of a probe run?

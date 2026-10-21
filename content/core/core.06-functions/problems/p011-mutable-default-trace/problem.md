# What the default remembers

Predict **exactly** what this program prints. Keep a drawing of `remember.__defaults__` on
paper and update it after every call.

```python
def remember(item, seen=[], count=0):
    seen.append(item)
    count += 1
    return len(seen), count

print(remember.__defaults__)
print(remember("a"))
print(remember("b"))
print(remember("c", []))
print(remember("d", count=10))
print(remember.__defaults__)

def start(item, seen=None):
    seen = seen or ["start"]
    seen.append(item)
    return seen

print(start("x"))
print(start("y"))
mine = []
print(start("z", mine), mine)
```

Write your answer in `answer.txt`, one line per printed line.

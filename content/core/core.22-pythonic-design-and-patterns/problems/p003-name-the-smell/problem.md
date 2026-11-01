# Explain: name the smell

A code smell is a small sign that something deeper may be wrong. Below are six short snippets.
For **each** one write three things: the **name** of the smell, **why it hurts** (what goes
wrong, or who suffers), and the **Pythonic fix** (a line or two of code).

```python
# 1
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags

# 2
try:
    price = float(text)
except:
    price = 0.0

# 3
def total(x):
    if type(x) == list:
        return sum(x)
    return x

# 4
report = ""
for row in rows:
    report += row.name + ": " + str(row.score) + "\n"

# 5
l = []
for o in orders:
    if o.paid:
        l.append(o)

# 6
def find_user(users, name):
    for u in users:
        if u.name == name:
            return u
    return False
```

Write `answer.md`: one short paragraph or bullet per snippet (about 250 to 350 words in all).

**Example of the level of detail expected (a different snippet)**

> `if len(items) == 0:` **Smell:** checking emptiness the long way. **Hurts:** more to read, and
> it breaks for iterables with no `len`. **Fix:** `if not items:` (empty containers are falsy).

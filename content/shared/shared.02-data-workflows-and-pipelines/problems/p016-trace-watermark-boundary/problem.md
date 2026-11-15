# Trace: > versus >= at the watermark

Three incremental loaders read the same changing source. They differ only in how they ask for
"what changed since my watermark":

- `gt` asks for `updated_at > watermark`,
- `ge` asks for `updated_at >= watermark`,
- `overlap` asks for `updated_at > watermark - 3` (it looks back 3 minutes on purpose).

Every loader upserts what it receives (so receiving a row twice never duplicates it) and then
sets its watermark to the largest `updated_at` it received. Timestamps are plain integers
(minutes) to keep the trace short.

The interesting moment is a **late arrival**: order 3 is committed on the server *after* run 1,
but its `updated_at` is 105, exactly the watermark run 1 stored.

Work out exactly what this program prints. The program needs no input.

```python
source = {1: 100, 2: 105}            # order id -> updated_at (in minutes)


def fetch(since, mode):
    """The fake API: which ids does it return for updated_since=since?"""
    if since is None:
        return sorted(source)
    if mode == "gt":
        return sorted(i for i, t in source.items() if t > since)
    if mode == "ge":
        return sorted(i for i, t in source.items() if t >= since)
    return sorted(i for i, t in source.items() if t > since - 3)   # "overlap": look back 3


class Loader:
    def __init__(self, mode):
        self.mode = mode
        self.wm = None                # the watermark
        self.table = {}               # our copy: id -> updated_at

    def run(self):
        ids = fetch(self.wm, self.mode)
        changed = 0
        for i in ids:
            if self.table.get(i) != source[i]:
                changed += 1          # an insert or a real update
            self.table[i] = source[i] # upsert
        if ids:
            self.wm = max(source[i] for i in ids)
        print(self.mode, ids, changed, self.wm)


loaders = [Loader("gt"), Loader("ge"), Loader("overlap")]


def run_all(label):
    print("--", label)
    for loader in loaders:
        loader.run()


run_all("run 1")
source[3] = 105                       # committed late, with the same time as order 2
source[4] = 107
run_all("run 2")
run_all("run 3")
source[2] = 109                       # order 2 is changed
source[5] = 103                       # arrives very late, older than every watermark
run_all("run 4")
for loader in loaders:
    missing = sorted(set(source) - set(loader.table))
    stale = sorted(i for i in loader.table if loader.table[i] != source[i])
    print(loader.mode, "missing", missing, "stale", stale)
```

Write your answer in `answer.txt`, one output line per `print`, exactly as Python prints it
(lists print like `[1, 2]`, an empty list as `[]`).

**Example (a different program)**

```python
source = {1: 10, 2: 20}
wm = 10
print([i for i, t in source.items() if t > wm], [i for i, t in source.items() if t >= wm])
```

prints

```
[2] [1, 2]
```

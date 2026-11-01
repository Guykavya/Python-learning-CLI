# Explain: review this function

A teammate sends you this function in a pull request. It "works" (they ran it once). You are
the reviewer, and you may not just say "ugly".

```python
import json

LOG = []


def do_stuff(d, f, x):
    # open the file
    fh = open(f)
    # read the data
    data = json.load(fh)
    # loop over d
    for i in range(len(d)):
        # check x
        if x == True:
            # add the total
            d[i]["total"] = d[i]["price"] * d[i]["qty"] * data["rate"]
            LOG.append("done " + str(i))
        else:
            try:
                d[i]["total"] = d[i]["price"] * d[i]["qty"]
            except:
                d[i]["total"] = 0
                print("error")
    # print the result
    print("Total: " + str(sum([r["total"] for r in d])))
    return d
```

Write `answer.md` (about 300 to 400 words) with these parts:

1. **Problems**: list the distinct problems you see (at least six), each in a few words and
   with the reason it hurts a reader or a test.
2. **Names**: give better names for the function, `d`, `f`, `x` and the loop.
3. **Split**: say how you would split it into small functions (name them, say what each takes
   and returns, and which one is the only one that touches the file or prints).
4. **First test**: say what test you would write **first**, before changing anything, and why
   it comes first.

**Example of the level of detail expected (a different function)**

> *`def go(l): return [x*2 for x in l if x]`*: `go` and `l` tell the reader nothing (use
> `double_nonzero(numbers)`). `if x` also drops `0.0` silently, which may be intended or a bug,
> so I would ask. First test: pin today's behavior with `go([0, 1, 2]) == [2, 4]` before touching it.

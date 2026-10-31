# Rewrite unreadable code

This function from an old shop script works, and everybody is afraid to touch it:

```python
def s(r):
    d={}
    for x in r:
        if not x or x[0]=='#': continue
        p=x.split(',')
        if len(p)!=3: continue
        try: q=int(p[1]);c=float(p[2])
        except: continue
        if q<=0: continue
        k=p[0].strip().lower()
        d[k]=d.get(k,[0,0.0]); d[k][0]+=q; d[k][1]+=q*c
    return sorted(((k,v[0],round(v[1],2)) for k,v in d.items()),key=lambda t:(-t[2],t[0]))
```

Rewrite it in `solution.py` as `summarise_orders(rows: list[str]) -> list[tuple[str, int, float]]`
with clear names, a docstring, and **exactly the same behaviour on every input**, quirks
included. The tests run your function and the original side by side on many inputs, including
odd ones.

Your version must also:

- have a **docstring** that says what a row looks like and what is returned;
- catch only the exception that can really happen (**no bare `except:`**). A bare `except`
  also swallows `KeyboardInterrupt` and real bugs, so it hides problems while debugging.

Work like this: first **read** it and write down in plain words what each line does (what is a
row? when is it skipped? what is summed? how is it sorted?). Then try odd inputs on the original
in the REPL **before** writing your version: a blank line, `" #x,1,2"`, `"pen, 2 ,3.5"`,
`"pen,2.0,3"`, `"Pen,1,1"` and `"pen,1,1"` together, a negative quantity. That is how you
discover the quirks you must keep.

**Example**

```python
rows = [
    "# name,qty,price",
    "Pen,3,10.5",
    "book,1,120",
    "pen,2,10.5",
    "",
    "eraser,two,5",
]
summarise_orders(rows)
# [('book', 1, 120.0), ('pen', 5, 52.5)]
```

# Explain: read the profile

A colleague says "`shop.py` is slow, I think `parse` is the problem, let's rewrite it with a
regex". Before anyone rewrites anything, you profile it. Here is the program:

```python
import cProfile


def load(n):
    return [f"user{i % 400},{i % 7}" for i in range(n)]


def parse(line):
    name, value = line.split(",")
    return name, int(value)


def find_user(users, name):
    for user in users:
        if user == name:
            return user
    return None


def build(lines):
    users = []
    totals = {}
    for line in lines:
        name, value = parse(line)
        if find_user(users, name) is None:
            users.append(name)
        totals[name] = totals.get(name, 0) + value
    return totals


def main():
    lines = load(100_000)
    totals = build(lines)
    return sorted(totals.items())[:3]


cProfile.run("main()", sort="tottime")
```

And here is the real output of one run (Python 3.14 on a laptop; **the timings are
machine-specific** and change a little every run, the call counts never do):

```text
         400408 function calls in 0.577 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   100000    0.392    0.000    0.392    0.000 shop.py:13(find_user)
        1    0.075    0.075    0.548    0.548 shop.py:20(build)
   100000    0.044    0.000    0.063    0.000 shop.py:8(parse)
        1    0.027    0.027    0.027    0.027 shop.py:4(load)
   100000    0.019    0.000    0.019    0.000 {method 'split' of 'str' objects}
   100000    0.018    0.000    0.018    0.000 {method 'get' of 'dict' objects}
        1    0.002    0.002    0.577    0.577 <string>:1(<module>)
        1    0.000    0.000    0.577    0.577 {built-in method builtins.exec}
      400    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
        1    0.000    0.000    0.000    0.000 {built-in method builtins.sorted}
        1    0.000    0.000    0.576    0.576 shop.py:31(main)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        1    0.000    0.000    0.000    0.000 {method 'items' of 'dict' objects}
```

Answer in `answer.md` (about 250 to 350 words):

1. What do `tottime` and `cumtime` each measure? Use `build` as your example: why is its
   `tottime` 0.075 but its `cumtime` 0.548?
2. `main` has `tottime` 0.000 and `cumtime` 0.576. What does that tell you, and why is it **not**
   a sign that `main` should be optimised?
3. Why does `find_user` have the same `tottime` and `cumtime`? Its `percall` shows `0.000`: does
   that mean each call is free? Work out the real time per call.
4. Is your colleague right about `parse`? Even if a rewrite made `parse` **ten times** faster,
   roughly how much of the 0.577 s would you save?
5. Which function would you change, how, and roughly how fast do you expect the program to be
   afterwards? (The program has 400 different users.)

**Example of the level of detail expected** (for a line that is not in this profile):

> `1  0.000  0.000  0.300  0.300 app.py:3(run)`: `run` was called once and spent almost no time
> in its own lines; all 0.3 s were spent in functions it called.

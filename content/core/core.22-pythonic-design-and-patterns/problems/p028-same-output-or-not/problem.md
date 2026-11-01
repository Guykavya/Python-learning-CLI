# Trace: same output or not?

A refactor is only safe if the behavior stays the same. Below are five "before and after"
pairs, each one a tidy-up somebody was proud of. Some are true refactors and some quietly
change behavior. Work out what the whole program prints.

Hints about Python (not about the answer): a lambda looks up the variables of its enclosing
function **when it is called**; a default argument is evaluated **once**, when `def` runs;
a generator can be consumed **once**; `print(a, b)` evaluates both arguments first, then prints.

```python
# Pair 1: callbacks made in a loop
def before_1():
    callbacks = []
    for i in range(3):
        callbacks.append(lambda: i * 10)
    return [cb() for cb in callbacks]


def after_1():
    callbacks = [lambda i=i: i * 10 for i in range(3)]
    return [cb() for cb in callbacks]


# Pair 2: collecting items
def before_2(item, bag=[]):
    bag.append(item)
    return bag


def after_2(item, bag=None):
    if bag is None:
        bag = []
    bag.append(item)
    return bag


# Pair 3: reusing a sequence
def before_3():
    squares = (n * n for n in range(4))
    return sum(squares), max(squares, default=-1)


def after_3():
    squares = [n * n for n in range(4)]
    return sum(squares), max(squares, default=-1)


# Pair 4: a leftover loop variable
def before_4():
    i = 100
    squares = [i * i for i in range(3)]
    return i, squares


def after_4():
    i = 100
    squares = []
    for i in range(3):
        squares.append(i * i)
    return i, squares


# Pair 5: checking for None
def before_5(values):
    return [v == None for v in values]


def after_5(values):
    return [v is None for v in values]


print("1", before_1(), after_1())
print("2", before_2("a"), before_2("b"))
print("2", after_2("a"), after_2("b"))
print("3", before_3(), after_3())
print("4", before_4(), after_4())
print("5", before_5([None, 0, "", []]), after_5([None, 0, "", []]))
print("same" if before_1() == after_1() else "different")
print(before_2("c"), after_2("c"))
```

**Example**: line `4` prints a tuple of `(i, squares)` for `before_4()` and then for `after_4()`.
Both lists are `[0, 1, 4]`, but the first number is different: that difference is what
the pair is about, for you to find.

Write in `answer.txt` the lines the program prints, in order (eight lines).

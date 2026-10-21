# Chapter 4: Control flow and essential built-ins

Until now, your programs ran from the first line to the last, one line after another, every time. Real programs do not work like that. They make **decisions** ("is the password right?"), they **repeat** work ("for every line in the file..."), and they **stop early** when they have found what they need. The order in which lines actually run is called the **control flow** of a program. This chapter teaches every tool Python gives you to shape it.

The second half of the chapter covers a small set of built-in functions that work hand in hand with loops: `enumerate()`, `zip()`, `reversed()`, `any()`, `all()`, `sum()`, `min()` and `max()`. Good Python programmers use them all the time, because they replace several lines of fiddly loop code with one clear call. Finally, you will meet `match`/`case`, Python's structural pattern matching, which lets you check the *shape* of data and pull it apart in one step.

You already know `if` from earlier chapters in a basic form. Here we go much deeper: what Python really checks, how it decides, what happens inside a loop, and where the common traps are.

How to use this chapter:

- Type and run every example yourself. The output shown is the real output from Python 3.14.
- Answer every **Predict the output** question on paper before opening the answer. Getting it wrong is fine. Getting it wrong *and noticing* is how you learn.
- When an example crashes, the traceback is shown with the file path shortened to `example.py`.

## Table of contents

1. [Blocks and indentation](#1-blocks-and-indentation)
2. [if, elif and else](#2-if-elif-and-else)
3. [Truthiness in conditions](#3-truthiness-in-conditions)
4. [Conditional expressions](#4-conditional-expressions)
5. [Nested conditions versus flat logic](#5-nested-conditions-versus-flat-logic)
6. [Short-circuit evaluation in conditions](#6-short-circuit-evaluation-in-conditions)
7. [while loops](#7-while-loops)
8. [for loops and the idea of iteration](#8-for-loops-and-the-idea-of-iteration)
9. [range in depth](#9-range-in-depth)
10. [break, continue and pass](#10-break-continue-and-pass)
11. [The loop else clause](#11-the-loop-else-clause)
12. [Nested loops and loop design](#12-nested-loops-and-loop-design)
13. [enumerate()](#13-enumerate)
14. [zip()](#14-zip)
15. [reversed()](#15-reversed)
16. [A small preview: generator expressions](#16-a-small-preview-generator-expressions)
17. [any() and all()](#17-any-and-all)
18. [sum()](#18-sum)
19. [min() and max() with key and default](#19-min-and-max-with-key-and-default)
20. [Structural pattern matching: match and case](#20-structural-pattern-matching-match-and-case)
21. [Common loop patterns](#21-common-loop-patterns)
22. [Choosing between for and while](#22-choosing-between-for-and-while)
23. [Summary](#summary)
24. [Learning outcomes](#learning-outcomes)
25. [Module project](#module-project)
26. [Further reading](#further-reading)

---

## 1. Blocks and indentation

Every statement in this chapter has the same shape: a **header line** that ends with a colon `:`, followed by an **indented block** of one or more lines.

```
if temperature > 30:        <- header, ends with a colon
    print("Hot")            <- the block: every line indented the same amount
    print("Drink water")
print("Done")               <- back at the left edge: not part of the block
```

Many languages use curly braces `{ }` to mark where a block starts and ends. Python uses **indentation**, the spaces at the start of a line. The rule is simple: a block is all the lines that follow the header and are indented more than it, at the same level. The block ends at the first line that comes back to the header's level.

The standard (PEP 8) is **four spaces** per level. Your editor inserts them when you press Tab. Never mix tabs and spaces in one file.

### Under the hood

When Python reads your file, a part of it called the *tokenizer* turns changes in indentation into two invisible tokens, `INDENT` and `DEDENT`. The parser then treats those like opening and closing braces. So indentation is not decoration in Python. It is grammar. Wrong indentation is a `SyntaxError` or an `IndentationError` before the program even starts:

```python
x = 5
if x > 3:
print("big")
```

Output:

```text
  File "example.py", line 3
    print("big")
    ^^^^^
IndentationError: expected an indented block after 'if' statement on line 2
```

### Edge cases

- A block cannot be empty. If you need a block that does nothing, write `pass` (section 10).
- A one-line block may go on the header line: `if x > 3: print("big")`. This is legal but harder to read. Use it rarely.

---

## 2. if, elif and else

An `if` statement runs a block only when a condition is true.

```python
age = 20
if age >= 18:
    print("You can vote.")
print("Checked.")
```

Output:

```text
You can vote.
Checked.
```

Add `else` for the other case. Exactly one of the two blocks runs, never both, never neither:

```python
age = 15
if age >= 18:
    print("You can vote.")
else:
    print("Not yet.")
```

Output:

```text
Not yet.
```

When there are more than two possibilities, use `elif` (short for "else if"). You can have as many `elif` parts as you need, and the `else` at the end is optional.

```python
marks = 72
if marks >= 90:
    grade = "A"
elif marks >= 75:
    grade = "B"
elif marks >= 60:
    grade = "C"
else:
    grade = "F"
print(grade)
```

Output:

```text
C
```

### The rule that matters most: the first true condition wins

Python checks the conditions **from top to bottom** and stops at the **first** one that is true. It runs that block and then skips everything else in the chain. Later conditions are not even looked at.

This is why the order in the example above works. For 72, the check `marks >= 90` is false, `marks >= 75` is false, `marks >= 60` is true, so the grade is "C". We never had to write `marks >= 60 and marks < 75`, because if marks were 75 or more, an earlier branch would already have caught it.

Now see what happens when the order is wrong:

```python
marks = 95
if marks >= 60:
    grade = "C"
elif marks >= 75:
    grade = "B"
elif marks >= 90:
    grade = "A"
print(grade)
```

Output:

```text
C
```

95 is at least 60, so the first branch wins and the others never get a chance. When your conditions overlap, put the **most specific** (narrowest) one first.

### if versus a chain of separate ifs

Two separate `if` statements are **independent**. Both can run. An `if`/`elif` chain is **one** decision. At most one branch runs.

```python
n = 12
if n % 2 == 0:
    print("even")
if n % 3 == 0:
    print("multiple of 3")

if n % 2 == 0:
    print("even")
elif n % 3 == 0:
    print("multiple of 3")
```

Output:

```text
even
multiple of 3
even
```

Ask yourself: "Can more than one of these be true *and should all of them act*?" If yes, use separate `if`s. If only one should act, use `elif`.

### Under the hood

Python compiles an `if` statement into a test followed by a **jump**. In plain words: "work out the condition; if it is false, jump over the block to the next part." An `elif` chain is a series of these tests and jumps. That is why later conditions really are never evaluated once one succeeds: the program has already jumped past them.

### Predict the output

```python
x = 0
if x > 0:
    print("positive")
elif x == 0:
    print("zero")
elif x >= 0:
    print("not negative")
else:
    print("negative")
```

<details><summary>Answer</summary>

```text
zero
```

Both `x == 0` and `x >= 0` are true, but only the first true branch runs.

</details>

### Common misconceptions

- "`else` needs a condition." No. `else:` has no condition. It means "none of the above".
- "Python checks every `elif` and runs all the true ones." No. Only the first true one runs.
- Writing `if x == 1 or 2:`. This does not mean "x is 1 or 2". It means `(x == 1) or 2`, and `2` is truthy, so the condition is always true. Write `if x == 1 or x == 2:` or `if x in (1, 2):`.

```python
x = 7
if x == 1 or 2:
    print("x is 1 or 2?")
```

Output:

```text
x is 1 or 2?
```

### Edge cases

- `elif` and `else` must line up exactly with their `if`.
- A chain with no `else` may run no block at all. That is fine, but make sure it is what you want. If you assign a variable inside the branches, a chain with no `else` can leave the variable undefined:

```python
temperature = 20
if temperature > 30:
    message = "hot"
elif temperature < 10:
    message = "cold"
print(message)
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 6, in <module>
    print(message)
          ^^^^^^^
NameError: name 'message' is not defined
```

---

## 3. Truthiness in conditions

The condition of an `if` does not have to be a `bool`. Python accepts **any** object and asks it: "are you true or false?" You met this in Chapter 2 as *truthiness*. Here is the reminder.

These values are **falsy** (they count as false):

- `False` and `None`
- zero of any number type: `0`, `0.0`, `0j`, `Decimal("0")`, `Fraction(0)`
- empty collections and strings: `""`, `[]`, `()`, `{}`, `set()`, `range(0)`

**Everything else is truthy.** That includes `"0"`, `"False"`, `" "` (a space), `-1` and `[0]`.

So you can write:

```python
name = ""
if name:
    print("Hello,", name)
else:
    print("You did not type a name.")

words = "red green blue".split()
if words:
    print("First word:", words[0])
```

Output:

```text
You did not type a name.
First word: red
```

`if name:` reads as "if there is a name". This is the normal Python style. Writing `if len(name) > 0:` or `if name != "":` works, but is longer and says the same thing.

### A common input pattern

A line that contains only spaces is not empty, so it is truthy. When reading input, people usually want "blank" to include "only spaces". Strip first:

```python
line = "   "
if line:
    print("raw line is truthy")
if not line.strip():
    print("but it is blank after strip()")
```

Output:

```text
raw line is truthy
but it is blank after strip()
```

### Under the hood

When Python needs the truth of an object, it calls `bool()` on it. `bool()` first looks for a special method named `__bool__`. Numbers have one: it returns `False` for zero. If there is no `__bool__`, Python tries `__len__`, and an object whose length is 0 is falsy. That is why every empty container is falsy without anyone writing a special rule for it. If an object has neither method, it is truthy.

### When not to rely on truthiness

Truthiness merges several "nothing" values together. Sometimes that is wrong. Suppose `stock` can be `None` (meaning "unknown") or a number. Then `if not stock:` is true for **both** `None` and `0`, which mean very different things. Be explicit:

```python
stock = 0
if stock is None:
    print("stock unknown")
elif stock == 0:
    print("sold out")
else:
    print(stock, "left")
```

Output:

```text
sold out
```

### Predict the output

```python
for value in [0, "0", [], " ", None, -0.0, "None"]:
    if value:
        print(repr(value), "truthy")
    else:
        print(repr(value), "falsy")
```

(`repr()` shows a value the way you would type it, with quotes around strings. The `for` loop runs the block once for each value in the list. You will learn it properly in section 8.)

<details><summary>Answer</summary>

```text
0 falsy
'0' truthy
[] falsy
' ' truthy
None falsy
-0.0 falsy
'None' truthy
```

Only real zeros, empty things and `None` are falsy. `-0.0` is a zero. The strings `"0"`, `" "` and `"None"` are not empty, so they are truthy.

</details>

### Common misconceptions

- "`if x == True:` is the proper way." No. It is longer, and wrong for truthy values that are not exactly `True` (`2 == True` is `False`). Write `if x:`.
- "The string `"False"` is falsy." No. Only the empty string is falsy.

---

## 4. Conditional expressions

Sometimes you want to choose between two **values**, not between two blocks of code. Python has a one-line form for this, the **conditional expression** (other languages call it the "ternary operator"):

```
value_if_true if condition else value_if_false
```

```python
n = 1
print(f"{n} item" if n == 1 else f"{n} items")
n = 3
print(f"{n} item" if n == 1 else f"{n} items")

temperature = 34
label = "hot" if temperature > 30 else "fine"
print(label)
```

Output:

```text
1 item
3 items
hot
```

The reading order is a little unusual: the condition is in the **middle**. Read it as an English sentence: "label is *hot* if the temperature is above 30, else *fine*".

This is an **expression**: it produces a value. So you can use it anywhere a value fits: on the right of `=`, inside `print()`, inside an f-string, as an argument. An `if` *statement* cannot go in those places.

### Under the hood

Only one of the two values is evaluated. Python works out the condition first. If it is true, it evaluates the left value; otherwise it evaluates the right value. The other side never runs, so this is safe:

```python
count = 0
total = 50
average = total / count if count > 0 else 0
print(average)
```

Output:

```text
0
```

`total / count` would raise `ZeroDivisionError`, but it is never evaluated because the condition is false.

### Predict the output

```python
x = -4
print("neg" if x < 0 else "zero" if x == 0 else "pos")
x = 0
print("neg" if x < 0 else "zero" if x == 0 else "pos")
```

<details><summary>Answer</summary>

```text
neg
zero
```

Conditional expressions can be chained: the `else` part is itself another conditional expression. It works, but more than one level becomes hard to read. Prefer an `if`/`elif` statement then.

</details>

### Common misconceptions

- Forgetting the `else`. `x = 5 if flag` is a `SyntaxError`. A conditional expression must always produce a value, so the `else` is required.
- Using it for actions: `print("a") if ok else print("b")` works but is poor style. Use an `if` statement when you want to *do* something, and a conditional expression when you want to *pick a value*.

---

## 5. Nested conditions versus flat logic

You can put an `if` inside another `if`. This is called **nesting**.

```python
age = 25
has_ticket = True
if age >= 18:
    if has_ticket:
        print("Enter")
    else:
        print("Buy a ticket first")
else:
    print("Adults only")
```

Output:

```text
Enter
```

Nesting is fine for one or two levels. Deeper nesting quickly turns into code shaped like an arrow pointing to the right, where it is hard to see which `else` belongs to which `if`. Two techniques flatten it.

**Combine conditions with `and`.** When an inner `if` has no `else`, it can be merged with the outer one:

```python
if age >= 18:
    if has_ticket:
        print("Enter")
```

is the same as

```python
age = 25
has_ticket = True
if age >= 18 and has_ticket:
    print("Enter")
```

Output:

```text
Enter
```

**Handle the special cases first.** Check the "reject" cases at the top, each in its own branch, and leave the normal case for the end. This turns a deep tree into a flat list of rules, which matches how people describe rules in words:

```python
age = 16
has_ticket = True
if age < 18:
    print("Adults only")
elif not has_ticket:
    print("Buy a ticket first")
else:
    print("Enter")
```

Output:

```text
Adults only
```

Both versions behave the same. The flat one reads as a list: "under 18: refuse. No ticket: send away. Otherwise: let in."

### When nesting is right

Nesting is the clearer choice when an inner question only makes sense after an outer answer, and the inner part has several branches of its own. For example: first decide the vehicle type, then, inside each type, apply that type's own price rules. Forcing that into one flat chain would repeat the vehicle test in every line.

A useful test: if you find yourself writing the same condition in many branches (`if car and ...`, `elif car and ...`, `elif car and ...`), nesting may be clearer. If you find an `if` inside an `if` with no `else` anywhere, flatten it with `and`.

### Predict the output

```python
x = 5
if x > 0:
    if x > 10:
        print("big")
else:
    print("not positive")
print("end")
```

<details><summary>Answer</summary>

```text
end
```

The `else` lines up with `if x > 0`, so it belongs to the **outer** `if`. For x = 5 the outer condition is true, the inner one is false and has no `else`, so nothing is printed except `end`. Indentation decides which `if` an `else` belongs to.

</details>

---

## 6. Short-circuit evaluation in conditions

`and` and `or` evaluate their right side **only if they need to**:

- `A and B`: if `A` is falsy, the whole thing is already false. Python does not evaluate `B`.
- `A or B`: if `A` is truthy, the whole thing is already true. Python does not evaluate `B`.

This is called **short-circuit evaluation**. It is not only a speed trick. It lets the left side act as a **guard** that protects the right side from crashing.

```python
count = 0
total = 10
if count != 0 and total / count > 2:
    print("high average")
else:
    print("no average")

text = ""
if text and text[0] == "#":
    print("comment")
else:
    print("not a comment")
```

Output:

```text
no average
not a comment
```

If the order were swapped, `total / count` would run first and crash with `ZeroDivisionError`, and `text[0]` on an empty string would crash with `IndexError`. **Put the guard on the left.**

```python
text = ""
if text[0] == "#" and text:
    print("comment")
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    if text[0] == "#" and text:
       ~~~~^^^
IndexError: string index out of range
```

### Under the hood

As you learned in Chapter 2, `and` and `or` do not return `True` or `False`. They return **one of their operands**: `A and B` gives `A` if `A` is falsy, otherwise `B`. `A or B` gives `A` if `A` is truthy, otherwise `B`. In an `if`, Python then takes the truthiness of that result, so the effect is the same as a true/false answer.

That also gives a common idiom for defaults:

```python
name = ""
shown = name or "guest"
print(shown)
```

Output:

```text
guest
```

Be careful: it replaces *every* falsy value. `quantity or 1` turns a real `0` into `1`.

`not` always returns a real `bool`. Its precedence is lower than comparisons, so `not x == 5` means `not (x == 5)`.

### Predict the output

```python
a = 0
b = 3
print(a and b)
print(a or b)
print(b and a)
print(b or a)
print(not a, not b)
print(a != 0 and 6 // a > 1)
```

<details><summary>Answer</summary>

```text
0
3
0
3
True False
False
```

The last line is safe: `a != 0` is `False`, so `6 // a` is never evaluated, and `and` returns that `False`.

</details>

### Common misconceptions

- "Both sides of `and` are always evaluated." No. That is exactly what short-circuiting avoids.
- "`and` binds the same as `or`." No. `and` binds tighter: `a or b and c` means `a or (b and c)`. Use brackets when you mix them, for the reader's sake.

---

## 7. while loops

A `while` loop repeats its block **as long as** its condition is true.

```python
n = 3
while n > 0:
    print(n)
    n -= 1
print("Go!")
```

Output:

```text
3
2
1
Go!
```

The steps are always the same: (1) check the condition; (2) if it is false, leave the loop and continue after it; (3) if it is true, run the whole block, then go back to step 1. The condition is checked only at the **top**, once per round. If it becomes false in the middle of the block, the rest of the block still runs.

Each run through the block is called an **iteration**.

### Three things every while loop needs

1. A variable the condition depends on, **set before** the loop.
2. A condition that is true while there is work to do.
3. A line **inside** the block that changes that variable, so the condition can eventually become false.

Forget the third and you get an **infinite loop**: the condition stays true forever. If that happens, press **Ctrl+C** to stop the program. Python raises `KeyboardInterrupt` and ends.

### Sentinel loops

A **sentinel** is a special input value that means "stop", such as `done`, `0` or an empty line. The loop keeps reading until it sees the sentinel. The usual shape reads once before the loop and again at the end of each iteration:

```python
total = 0
line = input()
while line != "done":
    total += int(line)
    line = input()
print("Total:", total)
```

With the input lines `5`, `10`, `7`, `done`:

```text
Total: 22
```

Notice that `input()` appears **twice**: once before the loop, once at the bottom. The sentinel itself is never added, because the condition is checked right after each read.

### The loop-and-a-half: while True with break

Repeating `input()` in two places is a small duplication that can get out of step when you edit one copy. The alternative is to loop "forever" and leave from the **middle** with `break` (section 10 covers `break` fully):

```python
total = 0
while True:
    line = input()
    if line == "done":
        break
    total += int(line)
print("Total:", total)
```

With the same input:

```text
Total: 22
```

This is called a **loop-and-a-half**, because each iteration does "half" the work (reading) before deciding whether to continue. `while True:` looks dangerous, but it is a normal and clear Python idiom, as long as there is a `break` that will certainly be reached.

A classic use is asking until the input is valid:

```python
while True:
    text = input()
    if text.isdigit() and 1 <= int(text) <= 5:
        break
    print("Please type a whole number from 1 to 5.")
print("You chose", text)
```

With the input lines `abc`, `9`, `3`:

```text
Please type a whole number from 1 to 5.
Please type a whole number from 1 to 5.
You chose 3
```

Notice the short-circuit guard: `int(text)` is only evaluated when `text.isdigit()` is true, so `int("abc")` never crashes.

### Under the hood

A `while` loop compiles into a test at the top and a jump back to that test at the bottom. There is no counter and no hidden state. The loop knows nothing except its condition. That is its strength (it can express any kind of repetition) and its weakness (all the bookkeeping is yours).

### Predict the output

```python
i = 1
while i < 20:
    i *= 3
print(i)
```

<details><summary>Answer</summary>

```text
27
```

i goes 1, 3, 9, 27. When i is 9 the condition is still true, so the block runs and i becomes 27. Only then is the condition checked again. The variable after a loop is often past the limit.

</details>

### Common misconceptions and edge cases

- "The loop stops the moment the condition becomes false." No. It is only checked at the top of each iteration.
- A `while` loop whose condition is false at the start runs **zero** times. Always ask what happens then.
- Forgetting to update the variable, or updating the wrong one, gives an infinite loop.

---

## 8. for loops and the idea of iteration

A `for` loop runs its block **once for each item** in a collection of items:

```python
for ch in "cat":
    print(ch)

for word in "red green blue".split():
    print(word.upper())
```

Output:

```text
c
a
t
RED
GREEN
BLUE
```

You do not create, compare or increase a counter. The loop takes the items one by one and binds the **loop variable** (`ch`, `word`) to each in turn. When there are no more items, the loop ends.

Anything a `for` loop can walk through is called an **iterable**. You already know several: strings (character by character), the result of `split()` (word by word), and `range()` (number by number, next section). Later chapters add lists, tuples, dictionaries, sets and files.

### The loop variable is just a name

The loop variable is an ordinary variable. Each iteration **rebinds** it to the next item. Assigning to it inside the block does not change the collection and does not change what comes next:

```python
for n in range(3):
    print("got", n)
    n = 100
print("after:", n)
```

Output:

```text
got 0
got 1
got 2
after: 100
```

Also notice the last line: the loop variable **still exists after the loop**, holding the last value it was given (here, the 100 we assigned). If the loop ran zero times, the variable is never created at all.

### Under the hood: iter() and next()

A `for` loop is built on two built-in functions:

- `iter(x)` asks an iterable for an **iterator**: an object that remembers where it is in the sequence.
- `next(it)` asks the iterator for the next item. When there are none left, it raises `StopIteration`.

You can do by hand what `for` does for you:

```python
it = iter("hi")
print(next(it))
print(next(it))
print(next(it))
```

Output:

```text
h
i
Traceback (most recent call last):
  File "example.py", line 4, in <module>
    print(next(it))
          ~~~~^^^^
StopIteration
```

A `for` loop calls `iter()` once, then calls `next()` before every iteration, and quietly catches the `StopIteration` to end the loop. This one design is why `for` works with so many types: any object that can give an iterator can be looped over.

An important consequence: **an iterator can be used up**. Once it has given all its items, it is empty. Many built-ins in this chapter (`enumerate`, `zip`, `reversed`) return iterators, so you will meet this again.

### Predict the output

```python
count = 0
for ch in "banana":
    if ch == "a":
        count += 1
print(count, ch)
```

<details><summary>Answer</summary>

```text
3 a
```

Three `a`s. After the loop `ch` keeps the last character it was bound to.

</details>

### Common misconceptions

- "for loops need a counter, like in C." No. Python's `for` is a "for each" loop. Use `range()` only when you really want numbers.
- "Changing the loop variable skips items." No. The next iteration rebinds it from the iterator anyway.

---

## 9. range in depth

`range()` produces a sequence of whole numbers. It has three forms:

| Call | Numbers |
|---|---|
| `range(stop)` | 0, 1, ..., stop - 1 |
| `range(start, stop)` | start, start + 1, ..., stop - 1 |
| `range(start, stop, step)` | start, start + step, ... while still before stop |

The `stop` value is **never included**. The interval is *half-open*: it includes the start and excludes the stop.

```python
print(list(range(5)))
print(list(range(2, 6)))
print(list(range(0, 20, 5)))
print(list(range(1, 10, 3)))
```

Output:

```text
[0, 1, 2, 3, 4]
[2, 3, 4, 5]
[0, 5, 10, 15]
[1, 4, 7]
```

(`list()` collects all the values into a list so that we can print them in one go. Lists are the subject of the next chapter.)

### Why the stop is excluded

The half-open rule has nice properties. `range(n)` has exactly `n` numbers. `range(a, b)` has exactly `b - a` numbers. `range(len(s))` gives exactly the valid positions of a string `s`. And two ranges fit together without overlap or gap: `range(0, 5)` then `range(5, 10)`. The price is that you must write `range(1, n + 1)` to get 1 to n inclusive.

### Negative steps

With a negative step, `range` counts **down**, and it stops before reaching `stop` from above:

```python
print(list(range(5, 0, -1)))
print(list(range(10, -1, -2)))
print(list(range(3, -4, -3)))
```

Output:

```text
[5, 4, 3, 2, 1]
[10, 8, 6, 4, 2, 0]
[3, 0, -3]
```

To count from 5 down to **0** inclusive you need `range(5, -1, -1)`: the stop must be one step past the last number you want.

### Empty ranges

If the start is already at or past the stop in the direction of the step, the range is **empty** and a loop over it runs zero times. No error, no warning:

```python
print(list(range(5, 2)))
print(list(range(0, 5, -1)))
print(list(range(3, 3)))
for i in range(5, 2):
    print("never printed")
print("done")
```

Output:

```text
[]
[]
[]
done
```

The most common case is forgetting the negative step: `range(10, 0)` is empty, not a countdown.

A step of zero is not allowed:

```python
range(1, 10, 0)
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    range(1, 10, 0)
    ~~~~~^^^^^^^^^^
ValueError: range() arg 3 must not be zero
```

### Under the hood: range is lazy

A `range` object does **not** store its numbers. It stores only three integers, `start`, `stop` and `step`, and works out each number when asked. That is why `range(10**18)` is created instantly and uses almost no memory.

Because it knows those three numbers, a range can answer questions without looping:

```python
r = range(10, 100, 7)
print(r)
print(len(r))
print(r[0], r[3], r[-1])
print(31 in r, 32 in r)
print(r.start, r.stop, r.step)
big = range(10**18)
print(len(big), big[-1])
print(10**17 in big)
```

Output:

```text
range(10, 100, 7)
13
10 31 94
True False
10 100 7
1000000000000000000 999999999999999999
True
```

- `len(r)` is calculated with a formula from start, stop and step.
- `r[i]` is `start + i * step`, with negative indexes counted from the end, like strings.
- `x in r` for an integer is answered with arithmetic: is `x` between the ends, and is `(x - start)` divisible by `step`? It does not walk through a billion numbers.

A range can even be sliced, and the result is another range: `range(10)[2:8:2]` is `range(2, 8, 2)`.

### Predict the output

```python
r = range(20, 0, -6)
print(list(r))
print(len(r), r[-1])
print(2 in r, 0 in r)
print(len(range(7, 3)))
```

<details><summary>Answer</summary>

```text
[20, 14, 8, 2]
4 2
True False
0
```

From 20, step -6: 20, 14, 8, 2. The next would be -4, which is past the stop (0), so it stops. `range(7, 3)` with the default step +1 is empty.

</details>

### Common misconceptions

- "`range(1, 10)` includes 10." No. Stop is excluded.
- "`range(10, 1)` counts down." No. It is empty. Use a step of `-1`.
- "`range` makes a list." No. It is a small object that computes values on demand. `list(range(...))` makes a list.
- `range` only works with integers. `range(0, 1, 0.1)` is a `TypeError`.

---

## 10. break, continue and pass

These three statements change the normal flow inside a loop (`pass` works anywhere).

- `break` **leaves the loop immediately**. The rest of the block is skipped and no further iterations happen. Execution continues after the loop.
- `continue` **skips the rest of this iteration** and goes straight to the next one. In a `for` loop that means the next item; in a `while` loop that means checking the condition again.
- `pass` **does nothing at all**. It exists because a block cannot be empty.

```python
for ch in "py-thon!":
    if ch == "-":
        continue
    if ch == "!":
        break
    print(ch, end="")
print()
```

Output:

```text
python
```

The `-` is skipped by `continue`; the `!` stops the loop with `break`.

`continue` is useful for filtering at the top of a loop, so that the main work is not buried inside an `if`:

```python
for word in "apple # banana cherry # date".split():
    if word == "#":
        continue
    print(word)
```

Output:

```text
apple
banana
cherry
date
```

`pass` is a placeholder:

```python
for n in range(3):
    if n == 1:
        pass          # TODO: handle 1 later
    else:
        print(n)
```

Output:

```text
0
2
```

### Under the hood

`break` and `continue` are simply jumps: `break` to the first line after the loop, `continue` back to the top (the next `next()` call or the condition check). `pass` compiles to nothing.

### Edge cases and traps

- `break` and `continue` only affect the **innermost** loop that contains them. In nested loops, a `break` in the inner loop does not stop the outer one (section 12).
- A `continue` in a `while` loop that skips the line that updates the counter creates an infinite loop:

```
i = 0
while i < 5:
    if i == 2:
        continue      # i is never increased again!
    i += 1
```

Put the update **before** the `continue`, or use a `for` loop where the update is automatic.

- `break` outside a loop is a `SyntaxError`.

---

## 11. The loop else clause

Both `for` and `while` loops can have an `else` block. Its meaning surprises almost everyone the first time:

> The `else` block runs when the loop **finishes normally**, that is, **without hitting `break`**.

"Finishes normally" means a `for` loop ran out of items, or a `while` loop's condition became false. If the loop ends with `break`, the `else` is skipped.

This fits one very common job perfectly: **searching**. The loop looks for something and `break`s when it finds it. If it gets through everything without finding it, the `else` handles "not found".

```python
target = "o"
for i, ch in enumerate("python"):
    if ch == target:
        print("found at", i)
        break
else:
    print("not found")

for ch in "rhythm":
    if ch in "aeiou":
        print("has a vowel")
        break
else:
    print("no vowels at all")
```

Output:

```text
found at 4
no vowels at all
```

(`enumerate` gives both the position and the character; see section 13.)

Without `else` you would need a **flag** variable:

```python
found = False
for ch in "rhythm":
    if ch in "aeiou":
        found = True
        break
if not found:
    print("no vowels at all")
```

Output:

```text
no vowels at all
```

Both are correct. The loop `else` removes the flag, but only readers who know the rule understand it. Many programmers add a comment `# no break` next to the `else`. That is exactly what it means.

### It is not "else if the loop did not run"

The `else` also runs when the loop runs **zero** times, because a loop that never started also never hit `break`:

```python
for x in "":
    print("inside")
else:
    print("else runs for an empty loop too")

n = 0
while n > 0:
    n -= 1
else:
    print("while-else ran, n =", n)
```

Output:

```text
else runs for an empty loop too
while-else ran, n = 0
```

### Predict the output

```python
for n in range(3):
    if n == 5:
        break
    print(n, end=" ")
else:
    print("no break")

for n in range(3):
    if n == 1:
        continue
    print(n, end=" ")
else:
    print("still no break")
```

<details><summary>Answer</summary>

```text
0 1 2 no break
0 2 still no break
```

n never equals 5, so the first loop finishes normally. In the second loop, `continue` only skips one iteration; it is not a `break`, so the `else` still runs.

</details>

### Common misconceptions

- "The loop `else` runs if the loop body never ran." Partly true, but it also runs after a full, normal run. The only thing that skips it is `break` (or leaving by an error).
- "It pairs with an `if` inside the loop." No. It belongs to the `for` or `while`, and it must line up with that keyword. Indent it wrongly under the `if` and it becomes an ordinary `if`/`else`.

---

## 12. Nested loops and loop design

A loop inside another loop is a **nested loop**. For every single iteration of the outer loop, the inner loop runs **completely**.

```python
for row in range(1, 4):
    for col in "AB":
        print(f"{row}{col}", end=" ")
    print()
```

Output:

```text
1A 1B 
2A 2B 
3A 3B 
```

The outer loop ran 3 times. Each time, the inner loop ran 2 times. So the inner block ran 3 x 2 = 6 times. The `print()` after the inner loop (indented under the outer loop only) ends each row.

### break only leaves one loop

```python
for a in range(1, 4):
    for b in range(1, 4):
        if b > a:
            break
        print(a, b, end=" | ")
    print()
```

Output:

```text
1 1 | 
2 1 | 2 2 | 
3 1 | 3 2 | 3 3 | 
```

The `break` stops the inner loop early, but the outer loop keeps going. To stop **both** loops at once, the usual ways are a flag checked by the outer loop, or the `for`/`else` trick:

```python
for a in range(2, 10):
    for b in range(2, 10):
        if a * b == 42:
            print("found", a, b)
            break
    else:
        continue      # inner loop did not break: try the next a
    break             # inner loop did break: stop the outer loop too
```

Output:

```text
found 6 7
```

Later, when you learn functions, `return` will be the cleanest way to leave several loops at once.

### Designing a loop

Before you type a loop, answer these questions in words:

1. **What am I looping over?** Items of a string or a split line: use `for`. Numbers in a known range: `for` with `range`. "Until something happens": `while`.
2. **What do I need before the loop?** Counters at 0, totals at 0, flags at `False`, a "best so far" at the first item.
3. **What happens to one item?** Write the body for a single item first.
4. **When does it stop?** Naturally at the end, or early with `break`?
5. **What is true after the loop?** What does each variable mean now?
6. **What if there are zero items?** Does the code after the loop still print something sensible?

For nested loops, add: **does the inner loop depend on the outer variable?** In the `break` example above, the inner range really depends on `a`. Write that dependency into the inner loop's range when you can, instead of `break`: `for b in range(1, a + 1)` does the same job more clearly.

### Cost

Nested loops multiply. Two loops over 1,000 items each run the inner block a million times. That is fine. Three such loops would be a billion, which takes minutes. Notice this early; the DSA track studies it properly.

### Predict the output

```python
for i in range(3):
    for j in range(i):
        print(i, j)
print("i =", i)
```

<details><summary>Answer</summary>

```text
1 0
2 0
2 1
i = 2
```

When i is 0, `range(0)` is empty, so the inner loop does nothing. When i is 1, j takes 0. When i is 2, j takes 0 and 1. Three lines in total.

</details>

---

## 13. enumerate()

Often you need each item **and** its position. Programmers coming from other languages write this:

```python
word = "loop"
for i in range(len(word)):
    print(i, word[i])
```

Output:

```text
0 l
1 o
2 o
3 p
```

It works, but you manage an index you do not really care about, and `word[i]` repeats the name. `enumerate()` gives you both, directly:

```python
for i, ch in enumerate("loop"):
    print(i, ch)
```

Output:

```text
0 l
1 o
2 o
3 p
```

`enumerate(x)` produces **pairs**: (0, first item), (1, second item), and so on. The `for i, ch in ...` line unpacks each pair into two names.

Counting for humans usually starts at 1. Pass `start=`:

```python
for number, item in enumerate("milk bread eggs".split(), start=1):
    print(f"{number}. {item}")
```

Output:

```text
1. milk
2. bread
3. eggs
```

`start` only changes the **numbers** shown. It does not skip any items.

### Under the hood

`enumerate` is lazy. It does not build a list of pairs. It wraps the iterator of the thing you gave it and keeps a counter. Each `next()` asks the inner iterator for one item and returns `(counter, item)`, then adds 1 to the counter. So it works with anything iterable, even things that have no positions, like input lines read one at a time.

```python
e = enumerate("ab")
print(e)
print(next(e), next(e))
```

Output:

```text
<enumerate object at 0x7000befd9b20>
(0, 'a') (1, 'b')
```

The exact number after `at` changes every run. It is the object's address in memory.

### Common misconceptions

- "`enumerate(x, start=1)` skips the first item." No. All items appear; only the count starts at 1.
- Writing `for i, ch in "abc":` without `enumerate`. Python then tries to unpack each single character into two names and raises `ValueError`.

---

## 14. zip()

`zip()` walks through two or more iterables **side by side**, giving one item from each at a time:

```python
names = "Asha Ravi Meena".split()
scores = "82 91 77".split()
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

Output:

```text
Asha: 82
Ravi: 91
Meena: 77
```

The name comes from a zip fastener, whose two sides are joined tooth by tooth.

### Unequal lengths

By default, `zip` **stops at the shortest** input. Extra items in the longer ones are silently ignored:

```python
for a, b in zip("abcde", "12"):
    print(a, b)
```

Output:

```text
a 1
b 2
```

Silent dropping hides bugs. If the inputs *should* be the same length, pass `strict=True` (Python 3.10 and later). Then `zip` raises an error when one input runs out before the others:

```python
for a, b in zip("abc", "12", strict=True):
    print(a, b)
```

Output:

```text
a 1
b 2
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    for a, b in zip("abc", "12", strict=True):
                ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: zip() argument 2 is shorter than argument 1
```

Notice that the first two pairs were printed before the error. `zip` only discovers the problem when it reaches the end of the shorter input.

### Pairs of neighbours

A neat trick: zip a sequence with itself shifted by one, to visit each item together with the next one.

```python
temps = "30 32 31 35".split()
for today, tomorrow in zip(temps, temps[1:]):
    print(today, "->", tomorrow, int(tomorrow) - int(today))
```

Output:

```text
30 -> 32 2
32 -> 31 -1
31 -> 35 4
```

`temps[1:]` is everything but the first item. Slicing works on the result of `split()` just as on strings. Since the shifted copy is one shorter, `zip` stops at the right place: no index arithmetic and no off-by-one risk.

### Under the hood

Like `enumerate`, `zip` is a lazy iterator. Each `next()` call asks each input for one item, left to right. As soon as any input is exhausted, it stops. Because it is an iterator, it can be used only once:

```python
z = zip("ab", "xy")
print(list(z))
print(list(z))
```

Output:

```text
[('a', 'x'), ('b', 'y')]
[]
```

### Predict the output

```python
for i, (a, b) in enumerate(zip("hello", "hi"), start=1):
    print(i, a + b)
```

<details><summary>Answer</summary>

```text
1 hh
2 ei
```

`zip` stops after 2 pairs, because "hi" has only 2 characters. `enumerate` numbers those pairs from 1. The brackets in `(a, b)` unpack the inner pair.

</details>

---

## 15. reversed()

`reversed(x)` gives the items of a sequence from the **last to the first**:

```python
for ch in reversed("stressed"):
    print(ch, end="")
print()
for n in reversed(range(1, 6)):
    print(n, end=" ")
print()
words = "one two three".split()
for w in reversed(words):
    print(w, end=" ")
print()
```

Output:

```text
desserts
5 4 3 2 1 
three two one 
```

`reversed(range(1, 6))` is often clearer than working out `range(5, 0, -1)` yourself: say the range you mean, then reverse it.

### Under the hood

`reversed` does not copy the sequence. It returns an iterator that starts at the last position and walks backwards using indexes. That only works for things that know their length and support indexing, such as strings, ranges and lists. It does **not** work on a one-way iterator, which cannot go backwards:

```python
reversed(enumerate("abc"))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    reversed(enumerate("abc"))
    ~~~~~~~~^^^^^^^^^^^^^^^^^^
TypeError: 'enumerate' object is not reversible
```

`reversed()` returns an iterator, not a string. To get a reversed **string**, use slicing `s[::-1]` or `"".join(reversed(s))`.

---

## 16. A small preview: generator expressions

The next built-ins (`any`, `all`, `sum`, `min`, `max`) take an iterable and boil it down to one answer. Very often you want to give them not the raw items, but something worked out **from** each item: "is this character a digit?", "the length of this word". Python has a compact way to write that, called a **generator expression**:

```
(expression for name in iterable)
```

It reads like a `for` loop written backwards and squeezed onto one line. It produces the value of the expression for each item, lazily, one at a time. When it is the only argument of a function, you can drop its own brackets:

```python
word = "a1b2c3"
print(sum(1 for ch in word if ch.isdigit()))
print(sum(int(ch) for ch in word if ch.isdigit()))
print(any(ch.isupper() for ch in word))
```

Output:

```text
3
6
False
```

The optional `if` at the end filters the items. That is all you need for now. The full story (list, dict and set comprehensions, and generators) comes in the next chapters. Everything in this chapter can also be written as a plain `for` loop. Generator expressions are just shorter.

---

## 17. any() and all()

- `any(iterable)` is `True` if **at least one** item is truthy.
- `all(iterable)` is `True` if **every** item is truthy.

```python
password = "hello2you"
print(any(ch.isdigit() for ch in password))
print(all(ch.islower() for ch in password))
print(all(ch.isalnum() for ch in password))
print(any(ch.isupper() for ch in password))
```

Output:

```text
True
False
True
False
```

The second line is `False` because `"2"` is not lowercase. `"2".islower()` is `False`.

### Under the hood: they short-circuit

`any` stops at the **first truthy** item; `all` stops at the **first falsy** item. Each is just a loop with an early exit, like this:

```python
items = "x y 7 z".split()
result = False
for item in items:
    if item.isdigit():
        result = True
        break
print(result)
```

Output:

```text
True
```

That loop is exactly what `any(item.isdigit() for item in items)` does.

### The empty case

This is the most famous edge case in the chapter:

```python
print(any([]))
print(all([]))
print(all(ch.isdigit() for ch in ""))
```

Output:

```text
False
True
True
```

- `any` of nothing is `False`: there is no item that is true.
- `all` of nothing is `True`: there is no item that is false.

The second one feels odd, but it is the only consistent answer. `all` means "there is no counter-example", and an empty collection has no counter-examples. Mathematicians call this *vacuous truth*. "All the unicorns in this room are purple" is true, because there are no unicorns to check. The practical danger: `all(ch.isdigit() for ch in text)` says `True` for an empty `text`, so a "digits only" check accepts an empty input unless you also check `text` is not empty. (This is why the string method `"".isdigit()` returns `False`: it was designed with that extra check.)

### Predict the output

```python
print(any([0, "", None]))
print(any([0, "", "0"]))
print(all([1, "a", [0]]))
print(all(n % 2 == 0 for n in range(0, 10, 2)))
print(all(n > 100 for n in range(5, 1)))
```

<details><summary>Answer</summary>

```text
False
True
True
True
True
```

`"0"` is a non-empty string, so it is truthy. `[0]` is a list with one item, so it is truthy. The last range is empty, so `all` is `True`.

</details>

---

## 18. sum()

`sum(iterable)` adds up numbers. `sum(iterable, start)` begins from `start` instead of 0.

```python
print(sum(range(1, 101)))
print(sum(int(w) for w in "4 8 15 16 23 42".split()))
print(sum([0.5, 0.25], 10))
print(sum([]))
```

Output:

```text
5050
108
10.75
0
```

The sum of nothing is `0` (or `start`), which is usually what you want.

Two limits worth knowing:

- `sum` refuses to add strings. Use `"".join(...)` for that, which is much faster for long strings:

```python
print(sum(["a", "b"], ""))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    print(sum(["a", "b"], ""))
          ~~~^^^^^^^^^^^^^^^^
TypeError: sum() can't sum strings [use ''.join(seq) instead]
```

- Counting with `sum` works because `True` is 1 and `False` is 0 (Chapter 2): `sum(ch == "a" for ch in "banana")` is 3.

---

## 19. min() and max() with key and default

`min` and `max` return the smallest and largest item. They work in two ways: with several arguments, or with one iterable.

```python
print(max(3, 9, 4))
print(min("banana"))
print(max("pear apple fig".split()))
```

Output:

```text
9
a
pear
```

Strings compare **alphabetically, by character codes**, so `min("banana")` is `"a"` and the largest word is `"pear"`. Capital letters come before small ones in that order, which often surprises people: `max("Zoo", "apple")` is `"apple"`.

### key: compare by something else

`key=` takes a **function**. `min` and `max` call it on every item and compare the results instead of the items. They still return the original **item**, not the key result.

```python
words = "kiwi banana fig apple".split()
print(max(words, key=len))
print(min(words, key=len))
print(max("Zoo", "apple", key=str.lower))
print(max("-7 3 -10 5".split(), key=int))
print(min(-7, 3, -10, 5, key=abs))
```

Output:

```text
banana
fig
Zoo
5
3
```

Note that we pass `len`, not `len()`. We are handing over the function itself, for `max` to call later. `str.lower` is the `lower` method taken from the `str` type, and `int` turns each text item into a number just for comparing: the result is still the string `"5"`.

When two items tie, `min` and `max` return the **first** one they met. `max(["ab", "cd"], key=len)` returns `"ab"`.

When you learn functions, you will write your own key functions, often with the short `lambda` form. For now, built-in functions such as `len`, `abs`, `int` and `str.lower` cover a lot.

### default: what to return for an empty input

`min` and `max` of nothing make no sense, so they raise an error:

```python
print(max([]))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    print(max([]))
          ~~~^^^^
ValueError: max() iterable argument is empty
```

With `default=`, they return that value instead (this only works in the one-iterable form):

```python
print(max([], default="nothing"))
print(min("".split(), key=len, default=None))
```

Output:

```text
nothing
None
```

### Predict the output

```python
print(max("10 9 100".split()))
print(max("10 9 100".split(), key=int))
print(min("cab", "Cab", "bad"))
print(max(["ab", "cd", "e"], key=len))
```

<details><summary>Answer</summary>

```text
9
100
Cab
ab
```

Without a key, these are strings, so `"9"` beats `"100"` because `"9"` > `"1"` at the first character. With `key=int` they compare as numbers. `"C"` comes before every lowercase letter. `"ab"` and `"cd"` tie on length, and the first one wins.

</details>

---

## 20. Structural pattern matching: match and case

`match` (Python 3.10 and later) compares one value, the **subject**, against a list of **patterns**, top to bottom, and runs the block of the first pattern that fits.

```python
command = "stop"
match command:
    case "go":
        print("Moving")
    case "stop" | "halt":
        print("Stopping")
    case _:
        print("Unknown command:", command)
```

Output:

```text
Stopping
```

For simple values this looks like an `if`/`elif` chain. Its real strength is that a pattern can describe the **shape** of the data and pull out its parts at the same time. Let us go through the kinds of pattern.

### Literal patterns

A number, a string, `True`, `False` or `None` written in a `case` matches a subject **equal** to it. (`True`, `False` and `None` are compared with `is`.)

### The wildcard _

`case _:` matches **anything** and binds nothing. It plays the role of `else`. Put it last. If no case matches and there is no wildcard, the `match` simply does nothing; it is not an error.

### OR patterns

`|` inside a pattern means "or": `case "stop" | "halt":` matches either. (Do not confuse it with `or`, which is not allowed in a pattern.)

### Capture patterns

A bare name in a pattern **matches anything and binds the subject to that name**:

```python
value = 42
match value:
    case 0:
        print("zero")
    case other:
        print("something else:", other)
```

Output:

```text
something else: 42
```

### Guards

A **guard** is an `if` after the pattern. The case matches only if the pattern fits **and** the guard is true:

```python
n = -5
match n:
    case 0:
        print("zero")
    case x if x < 0:
        print("negative", x)
    case x:
        print("positive", x)
```

Output:

```text
negative -5
```

### Sequence patterns: the most useful kind

A pattern in square brackets matches a **sequence** of the right length and matches each element against a sub-pattern. This is perfect for commands typed as words, because `split()` gives a sequence:

```python
for line in ["go north", "take lamp", "drop", "look", "say hello there"]:
    match line.split():
        case ["look"]:
            print("You look around.")
        case ["go", direction]:
            print("You go", direction)
        case ["take" | "get", item]:
            print("You take the", item)
        case ["say", *words]:
            print("You say:", " ".join(words))
        case [verb, *rest]:
            print(f"I don't know how to {verb!r} with {len(rest)} extra word(s)")
```

Output:

```text
You go north
You take the lamp
I don't know how to 'drop' with 0 extra word(s)
You look around.
You say: hello there
```

Read the patterns carefully:

- `["look"]` matches a sequence of exactly one item equal to `"look"`.
- `["go", direction]` matches exactly two items, the first equal to `"go"`, and **captures** the second as `direction`.
- `["take" | "get", item]` combines an OR pattern inside a sequence.
- `["say", *words]` matches `"say"` followed by **any number** of items (zero or more), all collected into `words`. Only one starred name is allowed per sequence pattern.
- `[verb, *rest]` matches any sequence with at least one item.

`"drop"` alone did not match `["take" | "get", item]` (wrong word) or `["go", direction]` (wrong length), so it fell through to the last case. An empty input line gives `[]`, which matches only a pattern like `case []:`.

### Under the hood

A sequence pattern checks three things in order: is the subject a sequence, is the length right, and does each element match its sub-pattern. **Strings are deliberately not treated as sequences here**, even though they are iterable. `match "ab": case [a, b]:` does **not** match. This avoids surprises where a word would be split into letters. Match on `text.split()` or on a list of characters when you mean that.

Patterns are checked strictly top to bottom, so order matters as in an `if`/`elif` chain. Put specific patterns before general ones.

### Class patterns: a preview

A pattern can also check a **type**. `int()` matches any integer, `str()` any string. For these built-in types, writing a name inside the brackets captures the value:

```python
for item in [3, "three", 3.0, -1, None, True]:
    match item:
        case bool():
            print(item, "is a bool")
        case int(n) if n < 0:
            print(n, "is a negative int")
        case int(n):
            print(n, "is an int")
        case str(s):
            print(repr(s), "is a str")
        case None:
            print("nothing")
        case _:
            print(item, "is something else")
```

Output:

```text
3 is an int
'three' is a str
3.0 is something else
-1 is a negative int
nothing
True is a bool
```

`True` matched `bool()` because it was checked first. Since `bool` is a kind of `int`, putting `int(n)` first would have caught `True` as the integer 1. When you learn classes, class patterns will also let you match objects by their attributes.

### The capture-versus-constant trap

This is the most dangerous mistake with `match`. Suppose you store a value in a variable and try to match against it:

```python
QUIT = "q"
key = "x"
match key:
    case QUIT:
        print("Quitting")
    case _:
        print("Other key")
```

Output:

```text
  File "example.py", line 4
    case QUIT:
         ^^^^
SyntaxError: name capture 'QUIT' makes remaining patterns unreachable
```

Python refuses to run it. A bare name in a pattern is **always a capture**, never a comparison. `case QUIT:` does not mean "equal to the variable QUIT". It means "match anything and store it in a new variable called QUIT". Python noticed that this makes the next case unreachable and raised a `SyntaxError`.

If the capture is the **last** case, there is no error, and the bug is silent:

```python
QUIT = "q"
key = "x"
match key:
    case "h":
        print("Help")
    case QUIT:
        print("Quitting")
print("QUIT is now", QUIT)
```

Output:

```text
Quitting
QUIT is now x
```

The key `x` "matched" `QUIT`, the program quit, and the variable `QUIT` was **overwritten** with `"x"`.

The rule: **a name with a dot in it is a constant (compared with `==`); a name without a dot is a capture.** So constants must be written with a dot, such as an attribute of a module or class:

```python
class Keys:
    QUIT = "q"
    HELP = "h"

key = "x"
match key:
    case Keys.QUIT:
        print("Quitting")
    case Keys.HELP:
        print("Help")
    case _:
        print("Other key")
```

Output:

```text
Other key
```

(A `class` here is just a named container for the two constants. Classes are explained in a later chapter.) The simpler fix, when there are only a few constants, is to write the literal value, `case "q":`, or to use a guard, `case k if k == QUIT:`.

### Predict the output

```python
for data in [[1, 2], [1, 2, 3], [], "12", [5]]:
    match data:
        case []:
            print("empty")
        case [x]:
            print("one:", x)
        case [x, y]:
            print("two:", x + y)
        case [first, *others]:
            print("many, first", first, "then", len(others))
        case _:
            print("not a list pattern:", data)
```

<details><summary>Answer</summary>

```text
two: 3
many, first 1 then 2
empty
not a list pattern: 12
one: 5
```

The string `"12"` is not matched by any sequence pattern, so it reaches the wildcard.

</details>

### When to use match

Use `match` when you are checking the **shape** of data (how many words, which first word, what type) and pulling parts out. For plain range checks such as `marks >= 75`, an `if`/`elif` chain is clearer.

---

## 21. Common loop patterns

Most loops you will write follow a few patterns. The DSA problem-solving chapter studies them as problem-solving tools; here is how each one looks with the tools from this chapter.

**Accumulate.** Start with a neutral value and combine each item into it. With built-ins this is often a single call:

```python
prices = "120 45 80".split()
total = 0
for p in prices:
    total += int(p)
print(total, sum(int(p) for p in prices))
```

Output:

```text
245 245
```

Strings accumulate too: start from `""` and add pieces with `+=`.

**Count.** Start at 0 and add 1 when a condition holds:

```python
text = "the cat sat on the mat"
count = 0
for word in text.split():
    if word == "the":
        count += 1
print(count, sum(1 for w in text.split() if w == "the"))
```

Output:

```text
2 2
```

**Search with a flag, and early exit.** Look for something and stop as soon as it is found. Use a flag, `for`/`else`, or `any()`:

```python
codes = "A12 B07 X99 C33".split()
for position, code in enumerate(codes, start=1):
    if code.startswith("X"):
        print("first X code at position", position)
        break
else:
    print("no X code")
print(any(c.startswith("X") for c in codes))
```

Output:

```text
first X code at position 3
True
```

Early exit is not only faster. It also matters for correctness when items after the found one should not be processed, such as transactions after the account runs out of money.

**Best so far.** Keep the best item seen so far and replace it when a better one comes. With `max(..., key=...)` and `min(..., key=...)` this often becomes one line, as you saw in section 19.

**Pairs of neighbours.** Use `zip(items, items[1:])` instead of index arithmetic.

For each pattern, ask the zero case: what does your loop print when there are no items at all? `sum` gives 0, `any` gives `False`, `all` gives `True`, `max` crashes unless you give a `default`.

---

## 22. Choosing between for and while

| Situation | Use |
|---|---|
| You have a collection of items to visit | `for item in items` |
| You need numbers in a known range | `for i in range(...)` |
| You need items and positions | `for i, item in enumerate(items)` |
| You walk two sequences together | `for a, b in zip(xs, ys)` |
| You repeat until something happens, and you cannot know how many times | `while condition` |
| You read input until a sentinel or until it is valid | `while True` with `break` |

A good rule: **use `for` whenever you can say in advance what you are looping over**. It cannot go infinite, it cannot forget to update a counter, and it cannot be off by one at the end. Use `while` when the number of iterations depends on what happens inside the loop: reading until `done`, halving a number until it is small, asking until the answer is valid.

If you catch yourself writing `i = 0`, `while i < len(s):`, `i += 1`, you are writing a `for` loop the long way.

---

## Summary

- A block is the indented lines after a header ending in `:`. Indentation is grammar.
- `if`/`elif`/`else` checks conditions top to bottom and runs only the **first** true branch. Put narrow conditions first.
- Any object can be a condition. Falsy: `False`, `None`, zeros, empty strings and collections. Use `is None` when `None` and `0` mean different things.
- `a if cond else b` picks a value. Only the chosen side is evaluated.
- Flatten nested `if`s with `and` or by handling special cases first.
- `and`/`or` short-circuit. Put the guard on the left.
- `while` checks its condition at the top of each iteration. Sentinel loops and `while True` with `break` handle input of unknown length.
- `for` takes items from an iterable using `iter()` and `next()`. The loop variable is an ordinary name that survives the loop.
- `range(start, stop, step)` excludes `stop`, can count down with a negative step, can be empty, and is lazy: `len`, indexing and `in` are computed, not searched.
- `break` leaves the innermost loop; `continue` skips to the next iteration; `pass` does nothing.
- A loop's `else` runs when the loop ends **without `break`**, including when it runs zero times.
- Inner loops run completely for every outer iteration. Design a loop by naming what it visits, its starting values, its stop and its zero case.
- `enumerate(x, start=1)` gives positions and items; `zip` walks side by side and stops at the shortest unless `strict=True`; `reversed` walks a sequence backwards. All three return one-use iterators.
- `any` of nothing is `False`; `all` of nothing is `True`. Both short-circuit.
- `sum(x, start)` adds numbers. `min`/`max` accept `key=` (compare by a function's result, return the item) and `default=` (for empty input).
- `match` tries patterns top to bottom: literals, `_`, `|`, captures, guards, sequence patterns with `*rest`, class patterns. Strings are not sequence subjects. A bare name always captures; dotted names are constants.

## Learning outcomes

After this chapter you should be able to:

- [ ] Write `if`/`elif`/`else` chains in the right order and explain why only one branch runs.
- [ ] Use truthiness in conditions, and say when an explicit `is None` or `== 0` is better.
- [ ] Use conditional expressions to choose values, and flatten nested conditions.
- [ ] Use short-circuit evaluation to guard against crashes.
- [ ] Write sentinel loops and loop-and-a-half loops for input of unknown length.
- [ ] Explain how a `for` loop uses `iter()` and `next()`.
- [ ] Predict any `range()` including negative steps and empty ranges, and explain why range is lazy.
- [ ] Use `break`, `continue`, `pass` and loop `else` correctly, and explain exactly when `else` runs.
- [ ] Design nested loops and say how many times the inner block runs.
- [ ] Replace manual index loops with `enumerate`, `zip` and `reversed`, and handle unequal lengths with `strict=True`.
- [ ] Use `any`, `all`, `sum`, `min` and `max` with `key` and `default`, including on empty input.
- [ ] Use `match`/`case` to destructure commands, and avoid the capture-versus-constant trap.
- [ ] Choose between `for` and `while` and write loops without off-by-one errors.

## Module project

The project for this module is a **number guessing game and a menu-driven calculator**. The guessing game uses a `while` loop that reads guesses until the player wins or runs out of tries, with a loop `else` or a flag to report a loss, and it must reject input that is not a whole number without crashing. The calculator shows a menu, reads a choice in a loop-and-a-half, uses `match` to dispatch on the choice, guards against division by zero, and keeps a count of the calculations done. Problem p053 builds the core of the calculator; the project brief gives the full requirements.

## Further reading

All links are to the official Python documentation.

- More control flow tools (tutorial): https://docs.python.org/3/tutorial/controlflow.html
- The if statement: https://docs.python.org/3/reference/compound_stmts.html#the-if-statement
- The while statement: https://docs.python.org/3/reference/compound_stmts.html#the-while-statement
- The for statement: https://docs.python.org/3/reference/compound_stmts.html#the-for-statement
- The match statement: https://docs.python.org/3/reference/compound_stmts.html#the-match-statement
- match statements (tutorial): https://docs.python.org/3/tutorial/controlflow.html#match-statements
- Conditional expressions: https://docs.python.org/3/reference/expressions.html#conditional-expressions
- Boolean operations: https://docs.python.org/3/reference/expressions.html#boolean-operations
- Truth value testing: https://docs.python.org/3/library/stdtypes.html#truth-value-testing
- range: https://docs.python.org/3/library/stdtypes.html#ranges
- Built-in functions (enumerate, zip, reversed, any, all, sum, min, max): https://docs.python.org/3/library/functions.html
- Iterator types: https://docs.python.org/3/library/stdtypes.html#iterator-types

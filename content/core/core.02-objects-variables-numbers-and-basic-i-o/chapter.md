# Chapter 2: Objects, variables, numbers and basic I/O

In the first module you wrote tiny programs that printed text. In this chapter we slow down and look closely at the pieces those programs are made of. What exactly happens when you write `x = 5`? Why does `0.1 + 0.2` not equal `0.3`? Why is `-7 // 2` equal to `-4` and not `-3`? How do you read a number typed by the user, and what happens when they type something silly?

By the end you will have a clear mental model of objects and names, know Python's number types in depth, and be able to predict almost any expression built from these operators. Run every example yourself, and answer every "Predict the output" question before opening the answer.

A note on how examples are shown. A block of code is followed by the exact output it produces when run as a script with Python 3.14. When an example produces an error, Python prints a *traceback*. In a real traceback, the first `File "..."` line shows the full path of your file, such as `/home/you/python/example.py`. In this chapter the path is shortened to just `example.py`.

## Table of contents

1. [print() in depth](#1-print-in-depth)
2. [input(): reading text from the user](#2-input-reading-text-from-the-user)
3. [Converting input to numbers, and invalid input](#3-converting-input-to-numbers-and-invalid-input)
4. [Everything is an object: identity, type, value](#4-everything-is-an-object-identity-type-value)
5. [Names and binding: assignment is not copying](#5-names-and-binding-assignment-is-not-copying)
6. [Mutable and immutable objects](#6-mutable-and-immutable-objects)
7. [Integers: arbitrary precision](#7-integers-arbitrary-precision)
8. [Division, floor division and modulo](#8-division-floor-division-and-modulo)
9. [Floats and IEEE 754](#9-floats-and-ieee-754)
10. [Rounding errors, round() and math.isclose()](#10-rounding-errors-round-and-mathisclose)
11. [The decimal module](#11-the-decimal-module)
12. [The fractions module](#12-the-fractions-module)
13. [Complex numbers](#13-complex-numbers)
14. [bool is a kind of int](#14-bool-is-a-kind-of-int)
15. [None](#15-none)
16. [Truthiness, and, or, not](#16-truthiness-and-or-not)
17. [Operators and precedence](#17-operators-and-precedence)
18. [Chained comparisons](#18-chained-comparisons)
19. [Bitwise operators](#19-bitwise-operators)
20. [Type conversion rules](#20-type-conversion-rules)
21. [Augmented assignment](#21-augmented-assignment)
22. [The walrus operator :=](#22-the-walrus-operator-)
23. [is versus ==](#23-is-versus-)
24. [Summary](#summary)
25. [Learning outcomes](#learning-outcomes)
26. [Module project](#module-project)
27. [Further reading](#further-reading)

---

## 1. print() in depth

`print()` is a built-in function that turns its arguments into text and writes that text to the screen. You have used it already. Now let us look at every option it has.

The full shape of a call is:

```
print(value1, value2, ..., sep=" ", end="\n", file=sys.stdout, flush=False)
```

- You can pass **any number of values**, including zero. Each one is converted to text with `str()`.
- `sep` is the text placed **between** the values. The default is a single space.
- `end` is the text placed **after** the last value. The default is `"\n"`, a newline. This is why each `print()` normally starts a new line.
- `file` is **where** the text goes. The default is the screen (standard output).
- `flush` forces the text out immediately instead of letting it wait in a buffer.

`sep`, `end`, `file` and `flush` are *keyword arguments*. You must write their names, like `sep="-"`. If you wrote `print("a", "-")`, the `"-"` would just be another value to print.

```python
print("a", "b", "c")
print("a", "b", "c", sep="-")
print("a", "b", "c", sep="")
print(2026, 10, 18, sep="/")
print("Hello", end=" ")
print("World")
print("Loading", end="...")
print("done")
print()
print("x", 3, 2.5, True, None)
```

Output:

```text
a b c
a-b-c
abc
2026/10/18
Hello World
Loading...done

x 3 2.5 True None
```

Look at each line carefully:

- With `sep=""` the values are glued together.
- `print("Hello", end=" ")` did not finish the line, so the next `print` continued it.
- `print()` with no values prints just `end`, giving an empty line.

`sep` and `end` can be any string, including one with a newline:

```python
print("a", "b", sep="\n")
print("one", "two", sep=", ", end="!\n")
```

Output:

```text
a
b
one, two!
```

### Printing to standard error

A running program has two output channels. **Standard output** (`sys.stdout`) is for normal results. **Standard error** (`sys.stderr`) is for error messages and warnings. On your screen both look the same. The difference matters when output is redirected. For example, `python report.py > out.txt` sends standard output into the file, but error messages still appear on the screen, so you notice them.

```python
import sys
print("normal output")
print("error message", file=sys.stderr)
```

Output (both lines appear on the screen):

```text
normal output
error message
```

`import sys` makes the `sys` module available. Just copy that line when you need `sys.stderr`.

### flush, briefly

For speed, Python often collects printed text in a *buffer* and writes it out in bigger pieces. Normally you never notice. If you print a progress message with `end=""` and then the program does slow work, the message might not appear until later. `print("Working...", end="", flush=True)` forces it out at once. That is all you need to know about `flush` for now.

### Under the hood

- `print()` calls `str()` on every value. So `print(x)` shows exactly what `str(x)` returns.
- `print()` always **returns** `None`. It does its job as a side effect (writing text). It does not give back a value.

```python
x = print("hi")
print(x)
```

Output:

```text
hi
None
```

### Predict the output

```python
print(1, 2, 3, sep="")
print("1" + "2" + "3")
print(10, "apples", sep=" -> ", end=" |\n")
```

<details><summary>Answer</summary>

```text
123
123
10 -> apples |
```

Line 1 prints three numbers with nothing between them; line 2 joins three strings with `+`.

</details>

### Common misconceptions

- "`print` returns the thing it printed." No. It returns `None`.
- "`print(a, b)` puts no space between values." It does, because the default `sep` is `" "`.

---

## 2. input(): reading text from the user

`input()` pauses the program, waits for the user to type a line and press Enter, and then gives back what they typed.

```python
name = input("What is your name? ")
print("Hello,", name)
```

If the user types `Kavya`, the screen shows:

```text
What is your name? Kavya
Hello, Kavya
```

The text inside the brackets is the **prompt**. Python prints it (without a newline) and then waits. Notice the space at the end of `"What is your name? "`. Without it, the user's typing would be squashed against the question mark.

The prompt is optional. With no prompt, `input()` waits silently and the user sees only a blinking cursor. Always give a prompt when a human is using your program.

### The most important rule: input() always returns a str

Whatever the user types, even `42`, comes back as a **string**. `input()` never gives you a number.

```python
text = input("Enter your age: ")
print(type(text))
print(text + 1)
```

If the user types `20`:

```text
Enter your age: 20
<class 'str'>
Traceback (most recent call last):
  File "example.py", line 3, in <module>
    print(text + 1)
          ~~~~~^~~
TypeError: can only concatenate str (not "int") to str
```

`text` is the string `"20"`. You cannot add the number `1` to a string, so Python stops with a `TypeError`.

### Under the hood

- `input()` reads characters up to the Enter key. The newline character produced by Enter is **removed**. Everything else is kept exactly, including spaces at the start and end.
- If the user types `" 7 "` (space, seven, space), `input()` returns a string of length 3.
- If there is no more input at all (for example, the user presses Ctrl+D on Linux, or Ctrl+Z then Enter on Windows), `input()` raises `EOFError`.

### Predict the output

The user types `5` (and Enter) when this runs.

```python
text = input()
print(text * 2)
print(len(text))
```

<details><summary>Answer</summary>

```text
55
1
```

`text` is the string `"5"`. Multiplying a string by 2 repeats it, so you get `"55"`, not 10. The string has one character. Note there is no prompt, so the user sees only a cursor.

</details>

### Common misconceptions

- "If the user types a number, `input()` gives a number." Never. It is always `str`.

---

## 3. Converting input to numbers, and invalid input

To get a number, you **convert** the string with `int()` (whole numbers) or `float()` (numbers with a decimal point).

```python
age = int(input("Enter your age: "))
print("Next year you will be", age + 1)
```

The user types `20`:

```text
Enter your age: 20
Next year you will be 21
```

Read it inside out: `input(...)` returns the string `"20"`, `int("20")` makes the integer `20`, and `age` is bound to it.

A second example with `float()` and an f-string:

```python
price = float(input("Price: "))
qty = int(input("Quantity: "))
print(f"Total: {price * qty:.2f}")
```

The user types `19.99` and then `3`:

```text
Price: 19.99
Quantity: 3
Total: 59.97
```

Inside an f-string, `{value:.2f}` means "show this number with exactly 2 digits after the decimal point". `{value:,}` adds thousands separators. For example `f"{10**9:,}"` gives `1,000,000,000`, and `f"{1234567.891:,.2f}"` gives `1,234,567.89`.

### What happens with invalid input

Users make mistakes. Suppose the user types `twenty` into the age program above:

```text
Enter your age: twenty
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    age = int(input("Enter your age: "))
ValueError: invalid literal for int() with base 10: 'twenty'
```

Read the **last line first**:

- `ValueError` is the *kind* of error: the type was right (a string), but this value cannot be used.
- `invalid literal for int() with base 10: 'twenty'` says `int()` tried to read `'twenty'` as a base-10 (ordinary decimal) number and failed. The bad text is shown in quotes.
- The lines above tell you *where*: line 1 of your file, and the code on that line.

Here are other inputs that fail, with their exact messages:

| Code | Last line of the traceback |
|---|---|
| `int("3.5")` | `ValueError: invalid literal for int() with base 10: '3.5'` |
| `int("")` | `ValueError: invalid literal for int() with base 10: ''` |
| `int("12abc")` | `ValueError: invalid literal for int() with base 10: '12abc'` |
| `float("3.5.1")` | `ValueError: could not convert string to float: '3.5.1'` |

`int("")` happens when the user just presses Enter. `int("3.5")` surprises many people: `int()` reading a *string* accepts only whole-number text.

Some inputs that look odd are actually accepted:

```python
print(int("  42  "), int("-7"), int("+8"), float(" 2.5 "), float("1e3"), int("1_000"))
```

Output:

```text
42 -7 8 2.5 1000.0 1000
```

Both ignore surrounding spaces and accept a sign and underscores between digits. `float()` also accepts scientific notation: `1e3` means 1 times 10 to the power 3.

### Handling invalid input properly

For now, invalid input crashes your program. That is acceptable while learning, and the traceback tells you exactly what went wrong. To *catch* the error and ask again, you need `try`/`except` and loops, taught fully in module core.07. For now, learn to **recognise** these errors instantly.

### Under the hood

- `int(text)` reads text in base 10 by default. That is why the message says "with base 10". You can choose another base, which we will see in section 20.
- To accept `"3.5"` and get `3`, write `int(float("3.5"))`: first make a float, then `int()` chops off the fraction.

### Predict the output

```python
print(int(float("3.5")))
print(int(float("  -3.9 ")))
```

<details><summary>Answer</summary>

```text
3
-3
```

`int()` applied to a float *truncates*: it drops the fractional part and moves towards zero. So `-3.9` becomes `-3`, not `-4`.

</details>

### Common misconceptions

- "`int("3.5")` gives 3." No, it raises `ValueError`.
- "`int()` rounds." No, it truncates towards zero.

---

## 4. Everything is an object: identity, type, value

In Python, **every piece of data is an object**. The number `5` is an object. The string `"hello"` is an object. `True`, `None`, and even the `print` function are objects.

Every object has three properties:

1. **Identity.** Which object it is. You can think of it as the object's address in memory. The built-in `id()` returns a number for it. The identity never changes during the object's life.
2. **Type.** What kind of object it is. The built-in `type()` returns it. The type decides what you can do with the object (you can add two ints, you can uppercase a string). The type never changes during the object's life.
3. **Value.** The data it holds, such as `5` or `"hello"`.

```python
x = 10
print(type(x), x)
print(type(3.0), type("hi"), type(True), type(None), type(2+3j))
```

Output:

```text
<class 'int'> 10
<class 'float'> <class 'str'> <class 'bool'> <class 'NoneType'> <class 'complex'>
```

The word `class` here just means "type". In Python 3 these words mean the same thing.

If you `print(id(x))` you will see a large number such as `11370224`. The exact number is different on every computer and every run. Never write code that depends on the actual number. Use `id()` only to *compare* identities while learning.

### Under the hood

- In CPython (the standard Python you downloaded from python.org), `id()` happens to be the memory address of the object. Other Python implementations may use something else. The only promise is: two objects that exist at the same time have different ids.
- Types are objects too. `type(type(5))` is `<class 'type'>`.
- When nothing refers to an object any more, Python may destroy it and reuse its memory, so a later object can get the same id.

### Common misconceptions

- "Variables have types." In Python, *objects* have types. A name is just a label and can point to an object of any type. More on this next.

---

## 5. Names and binding: assignment is not copying

Here is the most important idea in this chapter. In Python, a variable is a **name** that refers to an object. It is not a box that contains a value.

Think of objects as things sitting on a table, and names as **sticky notes** you stick onto them. The statement

```
x = 5
```

means: "evaluate the right-hand side, which gives the int object `5`; then stick the label `x` onto that object". This is called **binding** the name `x` to the object.

Now consider:

```
b = a
```

This does **not** copy anything. It means: "find the object that `a` is stuck to, and stick the label `b` onto the same object". After this line, one object has two labels.

```python
a = 5
b = a
print(a is b)
a = a + 1
print(a, b)
print(a is b)
```

Output:

```text
True
6 5
False
```

Step by step:

1. `a = 5`: label `a` on object `5`.
2. `b = a`: label `b` on the same object. `a is b` is `True` (the `is` operator checks "same object?").
3. `a = a + 1`: Python computes `a + 1`, which creates (or finds) a *new* object `6`. Then the label `a` is **moved** to that new object. The object `5` is not changed at all. `b` is still stuck to `5`.

So assignment never changes an object. It only moves a label.

### Why this matters: shared objects

With numbers you never see a difference, because a number object can never be changed. But a **list** *can* be changed in place. Lists are taught in core.05; here is a quick preview:

```python
a = [1, 2]
b = a
b.append(3)
print(a)
```

Output:

```text
[1, 2, 3]
```

We changed the list through the name `b`, and the change is visible through `a`. That is because there was only ever **one** list, with two labels on it. `b = a` did not make a copy.

### Under the hood

- Python keeps a table mapping names to objects. Assignment updates that table.
- A name can be re-bound to an object of a different type at any time: `x = 5` and later `x = "five"` is fine. This is called *dynamic typing*.
- Using a name that has never been bound raises `NameError: name 'x' is not defined`.
- `x = y = 0` binds both names to the same object `0`.

### Predict the output

```python
x = y = 0
x += 1
print(x, y)
```

<details><summary>Answer</summary>

```text
1 0
```

Both labels start on `0`. `x += 1` computes a new object `1` and moves only the label `x`. `y` stays on `0`.

</details>

### Common misconceptions

- "`b = a` copies the value." No. It shares the object.
- "Changing `a` changed `b`." With `a = a + 1`, nothing was changed; a label was moved. Only operations that *modify an object in place* (like `append` on a list) are visible through other names.

---

## 6. Mutable and immutable objects

An object is **mutable** if its value can change after it is created. It is **immutable** if it can never change.

| Immutable (cannot change) | Mutable (can change in place) |
|---|---|
| `int`, `float`, `complex`, `bool` | `list` (core.05) |
| `str` | `dict` (later module) |
| `tuple` (later module) | `set` (later module) |
| `None`, `Decimal`, `Fraction` | |

Every type in this chapter is immutable, so every operation on a number or string produces a **new** object.

```python
s = "hello"
t = s.upper()
print(s, t)
```

Output:

```text
hello HELLO
```

`s.upper()` did not change `s`. It built a brand new string and returned it.

### Under the hood

- Immutability makes sharing safe: nobody can change a shared `5`. So Python sometimes reuses immutable objects instead of creating new ones (see section 23). Never depend on that.

### Common misconceptions

- "`x = x + 1` changes the number." No. Numbers are immutable. A new number object is created and `x` is re-bound.
- "Strings are mutable because I can do `s = s + "!"`." That creates a new string and moves the label.

---

## 7. Integers: arbitrary precision

The `int` type holds whole numbers: `0`, `-17`, `2026`. In many languages an integer has a fixed size, such as 32 or 64 bits, and silently "wraps around" when it gets too big. Python's `int` has **no fixed size**. It grows as large as your computer's memory allows. This is called *arbitrary precision*.

```python
x = 2**100
print(x)
print(type(x))
print(len(str(2**1000)))
```

Output:

```text
1267650600228229401496703205376
<class 'int'>
302
```

`2**1000` has 302 digits, and every one is exact.

You can write integer literals in other bases and with underscores for readability: `0b1010` (binary, 10), `0o17` (octal, 15), `0xff` (hexadecimal, 255), `1_000_000` (one million).

### Under the hood

- CPython stores a big int as a sequence of "digits" in base 2 to the power 30. Huge numbers use many digits: slower, but always exact.
- **Aside: the 4300-digit limit.** Converting a huge int to a decimal string (or a string to an int) is slow for very large numbers. Attackers could abuse that with giant inputs. So since Python 3.11, converting an int with more than 4300 decimal digits to or from a string raises an error by default. The calculation itself is fine; only the *conversion to text* is limited.

```python
print(len(str(10**4300)))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    print(len(str(10**4300)))
              ~~~^^^^^^^^^^
ValueError: Exceeds the limit (4300 digits) for integer string conversion; use sys.set_int_max_str_digits() to increase the limit
```

`10**4300` has 4301 digits, one more than the limit. As the message says, `sys.set_int_max_str_digits()` can raise the limit (passing `0` removes it). You will rarely need this.

### Common misconceptions

- "Integers overflow at about 2 billion." Not in Python.
- "Big ints lose precision." No. Only floats lose precision.

---

## 8. Division, floor division and modulo

Python has two division operators.

- `/` is **true division**. It always returns a `float`, even if the answer is whole: `8 / 2` is `4.0`.
- `//` is **floor division**. It divides and then rounds **down** (towards negative infinity) to a whole number.

`%` is **modulo**. It gives the remainder that goes with floor division.

With positive numbers this is what you learned in school: `7 // 2` is `3` and `7 % 2` is `1`, because 7 = 3 × 2 + 1.

With negative numbers you must be careful.

```python
print(7 // 2, 7 % 2)
print(-7 // 2, -7 % 2)
print(7 // -2, 7 % -2)
print(-7 // -2, -7 % -2)
print(int(-7 / 2), -7 / 2)
```

Output:

```text
3 1
-4 1
-4 -1
3 -1
-3 -3.5
```

Why is `-7 // 2` equal to `-4`? The exact answer is `-3.5`, and "floor" means round **down**, towards negative infinity. The next whole number below `-3.5` is `-4`.

Compare the last line: `int(-7 / 2)` gives `-3`. That is because `int()` **truncates** (rounds towards zero), while `//` **floors** (rounds towards negative infinity). For positive numbers they agree. For negative numbers they differ.

### The identity that ties them together

Python guarantees this identity for any numbers `a` and `b` (with `b` not zero):

```
(a // b) * b + (a % b) == a
```

So once you know `a // b`, the remainder is forced. For `-7` and `2`: `-7 // 2` is `-4`, and `-4 * 2` is `-8`, so the remainder must be `-7 - (-8) = 1`.

A consequence: **the result of `%` always has the sign of the divisor** (the right-hand number), or is zero. With a positive divisor, `a % b` is always between `0` and `b - 1`. So `-1 % 10` is `9`, which is handy for "wrap-around" counting, like a clock.

```python
print(-1 % 10, 23 % 10, -23 % 10)
print(divmod(17, 5), divmod(-17, 5))
a, b = -17, 5
print((a // b) * b + a % b == a)
print(7.5 // 2, 7.5 % 2, -7.5 // 2)
```

Output:

```text
9 3 7
(3, 2) (-4, 3)
True
3.0 1.5 -4.0
```

`divmod(a, b)` returns both results together as a pair: `(a // b, a % b)`. The line `a, b = -17, 5` binds two names at once. `//` and `%` also work on floats, and then the results are floats.

Dividing by zero with `/`, `//` or `%` raises `ZeroDivisionError: division by zero`.

### Under the hood

Why did Python choose flooring? Because it makes `%` behave nicely: with a positive divisor, the remainder is never negative. Languages like C and Java truncate instead, so in those languages `-7 % 2` is `-1`. If you translate code between languages, watch for this.

### Predict the output

```python
print(-13 // 4, -13 % 4)
print(13 // -4, 13 % -4)
print(divmod(-9, 3))
```

<details><summary>Answer</summary>

```text
-4 3
-4 -3
(-3, 0)
```

`-13 / 4` is `-3.25`; floor gives `-4`; then `-4 * 4 = -16`, so the remainder is `-13 - (-16) = 3`. For `13 // -4`, the exact answer is `-3.25`, floor is `-4`, `-4 * -4 = 16`, remainder `13 - 16 = -3` (negative, matching the negative divisor). `-9` divides evenly by `3`, so the remainder is `0`.

</details>

### Common misconceptions

- "`//` throws away the fractional part." That is only true for positive results. It rounds *down*.
- "`%` takes the sign of the left number." In Python it follows the divisor.
- "`8 / 2` is `4`." It is `4.0`, a float.

---

## 9. Floats and IEEE 754

The `float` type holds numbers with a fractional part, like `3.14` or `-0.5`, and very large or very small numbers like `6.02e23`. Almost every computer stores floats using a standard called **IEEE 754 double precision**.

### How a float is stored

A float uses exactly **64 bits**, split into three parts:

| Part | Bits | Meaning |
|---|---|---|
| Sign | 1 | 0 for positive, 1 for negative |
| Exponent | 11 | Which power of 2 to multiply by |
| Mantissa (fraction) | 52 | The significant binary digits |

The value is roughly `sign × 1.mantissa × 2^exponent`. It is like scientific notation, but in base 2 instead of base 10. The mantissa gives 53 binary digits of precision (52 stored plus one hidden leading 1). That is about **15 to 17 significant decimal digits**.

Because there are only 64 bits, there is a finite number of floats. Most decimal numbers, including `0.1`, **cannot be stored exactly**. Python stores the closest float it can.

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(f"{0.1:.20f}")
```

Output:

```text
0.30000000000000004
False
0.10000000000000000555
```

Why? In base 10, `1/3` is `0.3333...` forever. In base 2, `1/10` is `0.000110011001100...` forever. So the stored `0.1` is slightly more than one tenth, and `0.2` is slightly off too. The errors add up, and the sum lands on the float just *above* the one nearest to `0.3`.

### repr: the shortest string that round-trips

If `0.1` is not exactly one tenth, why does `print(0.1)` show `0.1`? Because Python displays the **shortest** decimal string that, when read back, gives exactly the same float. For the stored value nearest to 0.1, that shortest string is `0.1`. For the result of `0.1 + 0.2`, no short string works, so Python shows `0.30000000000000004`.

### Special values: inf and nan

```python
print(float('1e308') * 10)
print(-float('1e308') * 10)
print(float('inf') - float('inf'))
nan = float('nan')
print(nan == nan, nan != nan, nan < 1, nan > 1)
```

Output:

```text
inf
-inf
nan
False True False False
```

- The largest float is about `1.8e308`. Multiplying past it gives `inf` (infinity). This is called *overflow*.
- `nan` means "not a number". It is the result of undefined operations like infinity minus infinity.
- `nan` is **not equal to anything, even itself**. Every ordinary comparison with `nan` is `False`, except `!=`, which is `True`. To test for nan, use `math.isnan(x)`.

### Under the hood

```python
import sys
print(sys.float_info.max)
print(sys.float_info.epsilon)
print(2.0 ** 53, 2.0**53 + 1, 2**53 + 1)
print((0.1).as_integer_ratio())
```

Output:

```text
1.7976931348623157e+308
2.220446049250313e-16
9007199254740992.0 9007199254740992.0 9007199254740993
(3602879701896397, 36028797018963968)
```

- `epsilon` is the gap between `1.0` and the next float above it.
- Above `2**53` floats cannot even represent every whole number. `2.0**53 + 1` gives back `2.0**53`. The int version stays exact.
- `as_integer_ratio()` shows the exact fraction a float stores. The stored "0.1" is really 3602879701896397 / 36028797018963968. The bottom number is 2 to the power 55. Every float is a fraction whose bottom is a power of 2.
- Note that `1e308 * 10` gives `inf`, but some operations raise an error instead. For example, `2.0 ** 10000` raises `OverflowError`, and `float(10**400)` raises `OverflowError: int too large to convert to float`. Dividing a float by zero raises `ZeroDivisionError` rather than giving `inf`.

### Common misconceptions

- "Floats are random." No. Each float is an exact binary fraction; the error comes from converting decimals to binary. The same calculation always gives the same result.
- "`print` shows the full stored value." It shows the shortest string that maps back to the same float.

---

## 10. Rounding errors, round() and math.isclose()

Small errors can grow when you repeat operations:

```python
print(1.1 * 3, 0.1 * 3)
```

Output:

```text
3.3000000000000003 0.30000000000000004
```

**Rule: never compare floats with `==`.** Ask "are they close enough?" instead.

### round() and banker's rounding

`round(x)` rounds to the nearest whole number and returns an `int`. `round(x, n)` rounds to `n` digits after the point and returns a float.

When a number is **exactly halfway**, Python rounds to the nearest **even** digit. This is called *round half to even* or *banker's rounding*. It avoids a bias: if you always rounded halves up, totals of many rounded numbers would drift upwards.

```python
print(round(2.5), round(3.5), round(0.5), round(1.5), round(-2.5))
print(round(3.14159, 2), round(1234.5678, -2), round(7.6), type(round(7.6)), type(round(7.6, 1)))
```

Output:

```text
2 4 0 2 -2
3.14 1200.0 8 <class 'int'> <class 'float'>
```

A negative `n` rounds to tens, hundreds and so on.

### Why round(2.675, 2) is 2.67

```python
print(round(2.675, 2))
print(f"{2.675:.30f}")
```

Output:

```text
2.67
2.674999999999999822364316059975
```

You might expect `2.68`, either by "half up" or by "half to even" (7 is odd, so the even choice is 8). But the float you typed as `2.675` is actually stored as `2.67499999...`. It is *below* the halfway point, so it correctly rounds down to `2.67`. This is not a bug in `round()`. It is the binary storage problem again.

### math.isclose()

```python
import math
print(math.isclose(0.1 + 0.2, 0.3))
print(math.isclose(100, 101, rel_tol=0.01))
print(math.isclose(100, 102, rel_tol=0.01))
print(math.isclose(1e-10, 0.0))
print(math.isclose(1e-10, 0.0, abs_tol=1e-9))
```

Output:

```text
True
True
False
False
True
```

`math.isclose(a, b)` checks whether two numbers are close **relative to their size**. The default relative tolerance `rel_tol` is `1e-09`, which means "equal in about the first 9 significant digits". `rel_tol=0.01` means "within 1 percent of the larger one".

The trap is **comparing with zero**. A relative tolerance of a percentage of zero is zero, so nothing is "relatively close" to `0.0` except `0.0` itself. For values near zero, you must also give an **absolute** tolerance with `abs_tol`. Then the test passes if the difference is within either tolerance.

### Under the hood

The exact rule is: `abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)`.

### Predict the output

```python
print(round(0.5) + round(1.5) + round(2.5))
print(0.1 * 3 == 0.3)
```

<details><summary>Answer</summary>

```text
4
False
```

`round(0.5)` is `0`, `round(1.5)` is `2`, `round(2.5)` is `2` (all go to the even neighbour), total `4`. The second line is the classic float error.

</details>

### Common misconceptions

- "`round()` always rounds .5 up." No, it rounds halves to even, and many "halves" are not exactly halves in binary.
- "Formatting with `:.2f` fixes the error." It only changes how the number is *shown*. The stored value is unchanged.

---

## 11. The decimal module

For money, you usually need decimal arithmetic that behaves exactly like arithmetic on paper. The `decimal` module provides the `Decimal` type, which stores numbers **in base 10**. So `0.1` is stored exactly.

```python
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
print(Decimal("19.99") * 3)
print(Decimal("1.10") + Decimal("2.205"))
```

Output:

```text
0.3
True
59.97
3.305
```

`from decimal import Decimal` makes the name `Decimal` available. A `Decimal` can be mixed with an `int`, but not with a float.

### Create Decimals from strings, not floats

```python
from decimal import Decimal
print(Decimal(0.1))
```

Output:

```text
0.1000000000000000055511151231257827021181583404541015625
```

`Decimal(0.1)` copies the float **exactly**, including its binary error. The error happened when Python read the float literal `0.1`, before `Decimal` was ever called. Always write `Decimal("0.1")`. User input is already a string, so `Decimal(input("Amount: "))` is perfect. An invalid string raises `decimal.InvalidOperation`.

### Rounding money with quantize

`quantize()` rounds a Decimal to a fixed number of places, given as a pattern. `Decimal("0.01")` means "two places".

```python
from decimal import Decimal, ROUND_HALF_UP
print(Decimal("2.675").quantize(Decimal("0.01")))
print(Decimal("2.665").quantize(Decimal("0.01")))
print(Decimal("2.665").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
```

Output:

```text
2.68
2.66
2.67
```

The default rounding for Decimal is also half to even (`ROUND_HALF_EVEN`). But now the halves are real halves, so `2.675` goes to `2.68` (8 is even) and `2.665` goes to `2.66` (6 is even). Most shops and school textbooks round halves **up**. Ask for that with `rounding=ROUND_HALF_UP`.

### Precision: getcontext().prec

```python
from decimal import Decimal, getcontext
print(Decimal(1) / Decimal(3))
getcontext().prec = 6
print(Decimal(1) / Decimal(3))
```

Output:

```text
0.3333333333333333333333333333
0.333333
```

Decimal arithmetic happens inside a *context* that sets the precision: the number of **significant digits** kept in results. The default is 28. `getcontext().prec = 6` changes it for the rest of the program. Note that precision counts significant digits, not decimal places. For a fixed number of decimal places, use `quantize`.

### Under the hood

- A Decimal stores a sign, some digits and a power of 10. `Decimal("3.10")` keeps its trailing zero (repr `Decimal('3.10')`), which suits money.
- Decimal is slower than float. Use it where base-10 exactness matters, such as money.
- Mixing with a float raises `TypeError: unsupported operand type(s) for +: 'decimal.Decimal' and 'float'`. This protects you from sneaking binary errors back in.

### Common misconceptions

- "`Decimal(0.1)` is exactly 0.1." No. Use the string `"0.1"`.
- "`prec = 2` means 2 decimal places." It means 2 significant digits.

---

## 12. The fractions module

`Fraction` stores an exact ratio of two integers. It is always kept in lowest terms.

```python
from fractions import Fraction
print(Fraction(1, 3) + Fraction(1, 6))
print(Fraction(6, 8))
print(Fraction("0.1") + Fraction("0.2") == Fraction("3/10"))
print(Fraction(1, 3) * 3, Fraction(3, 4).numerator, Fraction(3, 4).denominator)
print(float(Fraction(1, 3)), Fraction(1,2) + 1)
```

Output:

```text
1/2
3/4
True
1 3 4
0.3333333333333333 3/2
```

Like Decimal, a Fraction built from a float copies the float's exact binary value. `limit_denominator(n)` finds the closest fraction whose denominator is at most `n`:

```python
from fractions import Fraction
import math
print(Fraction(0.1))
print(Fraction(0.1).limit_denominator(1000))
print(Fraction(math.pi).limit_denominator(1000))
```

Output:

```text
3602879701896397/36028797018963968
1/10
355/113
```

Fractions are exact for `+ - * /`, but their numerators and denominators can grow huge in long calculations.

---

## 13. Complex numbers

Python has a built-in `complex` type for numbers with a real and an imaginary part. The imaginary unit (the square root of -1) is written with `j`, as engineers do: `3 + 4j`. The `j` must follow a number, so the unit alone is `1j`; plain `j` would just be a name.

```python
z = 3 + 4j
print(z, type(z), z.real, z.imag, abs(z), z.conjugate())
print(z * z.conjugate())
print(1j * 1j)
print(complex(2, -1), complex("1+2j"))
```

Output:

```text
(3+4j) <class 'complex'> 3.0 4.0 5.0 (3-4j)
(25+0j)
(-1+0j)
(2-1j) (1+2j)
```

- `.real` and `.imag` give the two parts, always as floats.
- `abs(z)` is the distance from zero: the square root of (3 squared + 4 squared) = 5.
- `.conjugate()` flips the sign of the imaginary part. `.conjugate` is a *method*, so it needs brackets; `.real` and `.imag` are plain attributes, with no brackets.

The `math` module works only with real numbers. `math.sqrt(-1)` raises `ValueError`. The `cmath` module has complex versions: `cmath.sqrt(-1)` gives `1j`.

### Under the hood

A complex number is stored as two floats, so it has the same rounding issues as floats. Complex numbers cannot be ordered: `(1+2j) < (2+3j)` raises `TypeError: '<' not supported between instances of 'complex' and 'complex'`. Equality (`==`) works fine.

---

## 14. bool is a kind of int

The `bool` type has exactly two values, `True` and `False`. Comparisons such as `3 > 2` produce them.

Surprisingly, `bool` is a **subclass** of `int`. That means every bool *is* an int: `True` behaves like `1` and `False` like `0` in arithmetic.

```python
print(True + True, True * 10, False - 1, 5 + True)
print(isinstance(True, int), issubclass(bool, int), type(True))
print(True == 1, False == 0)
print(sum([True, False, True, True]))
```

Output:

```text
2 10 -1 6
True True <class 'bool'>
True True
3
```

`isinstance(obj, T)` asks "is `obj` of type `T`, or of a subtype of `T`?". `type(True)` is still `bool`, a special kind of `int`. Summing booleans counts how many are true.

### Under the hood

This is historical: early Python used `1` and `0` for truth, and making the new bools ints kept old code working.

### Common misconceptions

- "`True` and `1` are different, so `True == 1` is `False`." It is `True`.

---

## 15. None

`None` is Python's way of saying "no value here". Its type is `NoneType`, and there is **exactly one** `None` object in a running program. Such a one-of-a-kind object is called a *singleton*.

You have met `None` already: `print()` returns it. Later you will see functions that return `None` when they have nothing to give back.

Because there is only one `None`, the correct test is an **identity** test with `is`:

```python
x = None
print(x is None, x is not None)
print(None == 0, None == False, bool(None))
```

Output:

```text
True False
False False False
```

`None` is not equal to `0`, `False` or `""`. It is only treated as false in a true/false context (next section).

### Under the hood

Why `is None` and not `== None`? `is` checks for that exact object and cannot be fooled, while `==` lets an object compare itself in whatever way its type defines. Style guides recommend `is None` and `is not None`.

---

## 16. Truthiness, and, or, not

Any object can be used where Python expects true or false. You can see the result with `bool(x)`. The values that count as **false** ("falsy") are:

- `False` and `None`
- zero of any number type: `0`, `0.0`, `0j`, `Decimal("0")`, `Fraction(0)`
- empty collections: `""` (empty string), `[]`, `()`, `{}`, `set()`, `range(0)`

**Everything else is true** ("truthy").

```python
print(bool(0), bool(0.0), bool(""), bool(None), bool([]))
print(bool(1), bool(-0.1), bool("0"), bool(" "), bool("False"), bool(float('nan')))
```

Output:

```text
False False False False False
True True True True True True
```

Note the traps: `"0"`, `" "` and `"False"` are non-empty strings, so they are true. `nan` is not zero, so it is true.

### and, or return one of their operands

You might expect `and` and `or` to return `True` or `False`. They don't. They return **one of the two operands**:

- `a or b`: if `a` is truthy, the result is `a`; otherwise the result is `b`.
- `a and b`: if `a` is falsy, the result is `a`; otherwise the result is `b`.
- `not a` always returns a real bool: `True` or `False`.

They also **short-circuit**: if the answer is already decided by `a`, Python does not evaluate `b` at all.

```python
print(0 or "default")
print("Kavya" or "anon")
print(0 and 5)
print(3 and 5)
print(0 or "" or None)
print(not 5, not 0, not "")
print(True or 1/0)
print(False and 1/0)
```

Output:

```text
default
Kavya
0
5
None
False True True
True
False
```

`True or 1/0` never computes `1/0`, so no error happens. But `False or 1/0` must evaluate `1/0`, and raises `ZeroDivisionError`.

A common use: `name = input("Name: ") or "anonymous"`. If the user just presses Enter, the empty string is falsy, so `name` becomes `"anonymous"`.

### Predict the output

```python
print(1 and 0 and 9)
print(None or 0)
print(1 or 2 and 0)
```

<details><summary>Answer</summary>

```text
0
0
1
```

`1 and 0` gives `0` (falsy), so the chain stops there. `None or 0`: `None` is falsy, so the result is the second operand, `0`. In the last line `and` binds more tightly than `or`, so it means `1 or (2 and 0)`, and `1` is truthy, so the result is `1`.

</details>

### Common misconceptions

- "`and`/`or` always return a bool." They return an operand.
- "`bool("0")` is `False`." Any non-empty string is true.

---

## 17. Operators and precedence

When an expression has several operators, **precedence** decides which is applied first, just like BODMAS in school maths. Here is the table for everything in this chapter, from **highest** (applied first) to **lowest**:

| Level | Operators | Meaning |
|---|---|---|
| 1 (highest) | `(...)` | Brackets |
| 2 | `x(...)`, `x.attr` | Calls, attribute access |
| 3 | `**` | Power |
| 4 | `+x`, `-x`, `~x` | Unary plus, minus, bitwise not |
| 5 | `*`, `/`, `//`, `%` | Multiply, divide, floor divide, modulo |
| 6 | `+`, `-` | Add, subtract |
| 7 | `<<`, `>>` | Bit shifts |
| 8 | `&` | Bitwise and |
| 9 | `^` | Bitwise xor |
| 10 | `\|` | Bitwise or |
| 11 | `<`, `<=`, `>`, `>=`, `==`, `!=`, `is`, `is not`, `in`, `not in` | Comparisons |
| 12 | `not` | Boolean not |
| 13 | `and` | Boolean and |
| 14 | `or` | Boolean or |
| 15 | `if ... else` | Conditional expression (later module) |
| 16 (lowest) | `:=` | Assignment expression (walrus) |

Operators on one level group **left to right**: `10 - 4 - 3` is `(10 - 4) - 3` = `3`. The exception is `**`, which groups **right to left**: `2 ** 3 ** 2` is `2 ** 9` = `512`.

Another special rule: `**` binds more tightly than a unary minus *on its left*. So `-2 ** 2` means `-(2 ** 2)`, which is `-4`. To square negative two, write `(-2) ** 2`.

```python
print(-2 ** 2, (-2) ** 2)
print(2 ** 3 ** 2, (2 ** 3) ** 2)
print(2 + 3 * 4, (2 + 3) * 4)
print(10 - 4 - 3, 100 / 10 / 5)
print(2 ** -1, 2 * -3)
print(1 + 2 * 3 ** 2 // 4 % 5)
```

Output:

```text
-4 4
512 64
14 20
3 2.0
0.5 -6
5
```

Work the last one out: `3 ** 2` is `9`. Then `*`, `//`, `%` are on the same level, left to right: `2 * 9 = 18`, `18 // 4 = 4`, `4 % 5 = 4`. Finally `1 + 4 = 5`.

Note also `2 ** -1`: a unary minus on the **right** of `**` is fine and applies to the exponent.

### Under the hood

Bit operators sit *between* arithmetic and comparisons, so `6 & 3 == 2` means `(6 & 3) == 2`, which is `True`. Legal, but confusing. When in doubt, **add brackets**.

### Common misconceptions

- "`-2 ** 2` is 4." It is `-4`.
- "`**` groups left to right like everything else." It groups right to left.

---

## 18. Chained comparisons

In maths you write `1 < x < 10`. Python allows exactly the same:

```python
x = 5
print(1 < x < 10)
```

Output:

```text
True
```

The rule: `a < b < c` means `a < b and b < c`, except that `b` is **evaluated only once**. Any number of comparisons can be chained: `a op1 b op2 c op3 d` means `a op1 b and b op2 c and c op3 d`. The chain stops at the first false link (short-circuit).

"Evaluated once" matters when the middle part does something. `1 < int(input("Number: ")) < 10` asks the user **once**. Writing it out by hand as two comparisons with two `input()` calls would ask twice.

### Surprising cases

Because chaining applies to *every* comparison operator, some chains look odd:

```python
print(1 < 3 > 2)
print(3 > 2 > 1, (3 > 2) > 1)
print(1 < 2 == True)
print((1 < 2) == True)
```

Output:

```text
True
True False
False
True
```

- `1 < 3 > 2` means `1 < 3 and 3 > 2`. Both are true. It does *not* compare `1` with `2`.
- `3 > 2 > 1` is `3 > 2 and 2 > 1`, which is `True`. But with brackets, `(3 > 2) > 1` first gives `True`, then `True > 1` is `1 > 1`, which is `False`.
- `1 < 2 == True` is a chain: `1 < 2 and 2 == True`. And `2 == True` is `2 == 1`, which is `False`.

### Common misconceptions

- "`a < b < c` is `(a < b) < c`." No, it is a chain with an implicit `and`.
- Comparing unrelated types with `<` fails: `1 < "2"` raises `TypeError: '<' not supported between instances of 'int' and 'str'`. (`==` between them is allowed and is simply `False`.)

---

## 19. Bitwise operators

Integers are stored in binary. Bitwise operators work on the individual bits. `bin(n)` shows the binary form as a string starting with `0b`.

| Operator | Name | Rule for each bit |
|---|---|---|
| `a & b` | and | 1 if both bits are 1 |
| `a \| b` | or | 1 if either bit is 1 |
| `a ^ b` | xor | 1 if the bits differ |
| `~a` | not | flips every bit |
| `a << n` | left shift | moves bits left by `n` (multiplies by 2 to the power `n`) |
| `a >> n` | right shift | moves bits right by `n` (floor-divides by 2 to the power `n`) |

```python
print(6 & 3, 6 | 3, 6 ^ 3, ~6, 1 << 4, 100 >> 2)
print(bin(6), bin(3), bin(6 & 3), bin(6 | 3), bin(6 ^ 3))
print(f"{6:08b}")
```

Output:

```text
2 7 5 -7 16 25
0b110 0b11 0b10 0b111 0b101
00000110
```

Line up the bits: `6` is `110`, `3` is `011`. And: `010` = 2. Or: `111` = 7. Xor: `101` = 5. The f-string format `08b` shows 8 binary digits padded with zeros.

### ~x equals -x - 1

Python ints behave as if negative numbers were stored in **two's complement** with an infinite number of leading 1 bits. Flipping all bits of `x` gives `-x - 1`. So `~6` is `-7`, `~0` is `-1`, and `~-1` is `0`. Note that `bin(-6)` shows `-0b110`: Python displays a minus sign rather than the infinite row of 1s.

### Useful tricks

```python
print(13 & 1, 14 & 1)
print(16 & 15, 12 & 11)
print((255).bit_length(), (256).bit_length(), (0).bit_length())
print(-17 >> 1)
```

Output:

```text
1 0
0 8
8 9 0
-9
```

- `n & 1` is the last bit: `1` for odd, `0` for even.
- `n & (n - 1)` clears the lowest 1 bit. It gives `0` exactly when `n` is a power of two (for positive `n`). 16 is a power of two; 12 is not.
- `n.bit_length()` is how many bits are needed to write `abs(n)` in binary. The brackets around `255` are needed: `255.bit_length()` is a syntax error, because `255.` reads as a float.
- `>>` on a negative number floors, just like `//`: `-17 >> 1` is `-17 // 2`, which is `-9`.

### Predict the output

```python
print(5 & 6, 5 | 6, 5 ^ 6, ~5)
```

<details><summary>Answer</summary>

```text
4 7 3 -6
```

`5` is `101`, `6` is `110`. And: `100` = 4. Or: `111` = 7. Xor: `011` = 3. `~5` is `-5 - 1` = `-6`.

</details>

### Common misconceptions

- "`^` means power." It is xor. Power is `**`. `2 ^ 3` is `1`.
- "`&` and `and` are the same." `&` works on bits of ints; `and` works on truthiness and returns an operand.

---

## 20. Type conversion rules

### Implicit conversion in arithmetic

When you mix number types in arithmetic, Python converts automatically to the "wider" type, in this order:

```
bool  ->  int  ->  float  ->  complex
```

```python
print(1 + 2.0, type(1 + 2.0))
print(1.5 + 2j, type(1.5 + 2j))
print(True + 2.5)
print(3 == 3.0, 1 == 1.0 == (1+0j))
```

Output:

```text
3.0 <class 'float'>
(1.5+2j) <class 'complex'>
3.5
True True
```

Python **never** converts automatically between strings and numbers. `"5" + 3` raises `TypeError: can only concatenate str (not "int") to str`. You must convert explicitly.

### Explicit conversion

```python
print(int(3.99), int(-3.99), int(2.5e3), float(7), complex(3))
print(float("inf"), float("-inf"), float("nan"), float("Infinity"))
print(int("1010", 2), int("ff", 16), int("FF", 16), int("0xff", 16), int("0xff", 0))
print(bool("False"), bool(""), bool("0"), bool(0))
print(str(42), str(3.0), str(True), str(None), str(1+2j))
```

Output:

```text
3 -3 2500 7.0 (3+0j)
inf -inf nan inf
10 255 255 255 255
True False True False
42 3.0 True None (1+2j)
```

The rules to remember:

- `int(some_float)` **truncates** towards zero; `int(some_string)` accepts only whole-number text.
- `int(text, base)` reads text in another base. Letters are allowed for bases above 10, in either case. With base 16 an optional `0x` prefix is allowed. Base `0` means "work out the base from the prefix".
- `float()` accepts `"inf"`, `"nan"` and `"Infinity"` in any case.
- `bool(text)` checks only whether the string is **empty**. `bool("False")` is `True`. To read yes/no input you must compare the text yourself, for example `answer == "yes"`.
- `str(x)` gives the text form of anything.

### Edge cases

| Code | Result |
|---|---|
| `int("ff")` | `ValueError: invalid literal for int() with base 10: 'ff'` |
| `int(float("inf"))` | `OverflowError: cannot convert float infinity to integer` |
| `int(3.5, 10)` | `TypeError: int() can't convert non-string with explicit base` |
| `float(10**400)` | `OverflowError: int too large to convert to float` |
| `float(10**16 + 1)` | `1e+16` (the `+ 1` is lost: too many digits for a float) |

---

## 21. Augmented assignment

`x += 1` is shorthand for `x = x + 1`. Every arithmetic and bitwise operator has an augmented form: `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`, `&=`, `|=`, `^=`, `<<=`, `>>=`.

```python
n = 7
n //= 2
print(n)
n **= 3
print(n)
n %= 5
print(n)
s = "ab"
s += "c"
print(s)
```

Output:

```text
3
27
2
abc
```

### Under the hood: rebinding versus mutating

For an **immutable** object, `x += 1` cannot change the object. So Python computes a new object and **rebinds** the name, exactly like `x = x + 1`:

```python
x = 10
before = id(x)
x += 1
print(x, id(x) == before)
```

Output:

```text
11 False
```

The id changed: `x` now refers to a different object.

For a **mutable** object like a list, `+=` is allowed to change the object **in place**, and lists do. A preview (lists come in core.05):

```python
a = [1, 2]
b = a
a += [3]
print(a, b, a is b)
c = [1, 2]
d = c
c = c + [3]
print(c, d, c is d)
```

Output:

```text
[1, 2, 3] [1, 2, 3] True
[1, 2, 3] [1, 2] False
```

With `+=` the single shared list grew, so `b` sees the change. With `c = c + [3]` a new list was built and only `c` moved to it. So `x += y` and `x = x + y` are *not always* the same.

### Edge case

The name must already exist. `x += 1` on an unbound `x` raises `NameError: name 'x' is not defined`.

---

## 22. The walrus operator :=

The **assignment expression** `name := value` binds a name **and** gives back the value, all inside a bigger expression. It is nicknamed the walrus operator because `:=` looks like a walrus's eyes and tusks.

A normal assignment `x = 5` is a *statement* and cannot appear inside an expression. The walrus fills that gap.

```python
print(n := 10)
print(n)
print((total := 3 + 4) * 2, total)
price = 250
print("Discount:", (d := price * 0.1), "Final:", price - d)
```

Output:

```text
10
10
14 7
Discount: 25.0 Final: 225.0
```

In the last example the discount is computed once, printed, stored in `d`, and reused. Arguments are evaluated left to right, so `d` exists when `price - d` runs.

### Rules

- `:=` has the **lowest** precedence of all. In `(total := 3 + 4) * 2` the brackets are essential: without them, `total` would be bound to the whole of `3 + 4 * 2`. Use brackets generously.
- It is **not allowed as a plain statement** on its own. You must use `=` there, or wrap it in brackets:

```python
x := 5
```

Output:

```text
  File "example.py", line 1
    x := 5
      ^^
SyntaxError: invalid syntax
```

`(x := 5)` on its own line is legal but pointless. The walrus is most useful with `if` and `while`, which you will meet from core.03, for example to read input and test it in one line.

### Predict the output

```python
print((x := 3) + (x := x + 1) + x)
```

<details><summary>Answer</summary>

```text
11
```

Left to right: the first walrus gives `3`, the second binds `x` to `4` and gives `4`, and the final `x` is `4`. Total `11`. Legal, but never write code like this.

</details>

---

## 23. is versus ==

- `a == b` asks: **do they have equal values?**
- `a is b` asks: **are they the very same object?** (Same identity, same `id()`.)

```python
x = [1]
y = [1]
print(x == y, x is y)
z = x
print(z is x)
```

Output:

```text
True False
True
```

`x` and `y` are two separate lists that happen to hold equal values. `z = x` puts a second label on the same list.

### Small-integer caching: never rely on it

In CPython, the integers from **-5 to 256** are created once when Python starts and reused every time. So any two names holding, say, `100` refer to the same object. Larger numbers made at run time are usually separate objects:

```python
x = 256
y = int("256")
print(x is y)
x = 257
y = int("257")
print(x is y, x == y)
```

Output:

```text
True
False True
```

Python may also reuse equal constants within one file, so `a = 1000` and `b = 1000` can give `a is b` as `True`. All of this is a **CPython implementation detail** that can change between versions. Never depend on it.

Python even warns you when you use `is` with a literal number or string:

```python
x = 5
print(x is 5)
```

Output:

```text
True
example.py:2: SyntaxWarning: "is" with 'int' literal. Did you mean "=="?
  print(x is 5)
```

The warning (with the offending line) goes to standard error. Python produces it while compiling the file, before the code runs, so in a terminal it usually appears *above* the program's output.

### The rule

- Use `==` to compare **values**: numbers, strings, almost everything.
- Use `is` only to test for **singletons**, mainly `x is None` and `x is not None`.

### Predict the output

```python
import math
print(math.nan is math.nan, math.nan == math.nan)
```

<details><summary>Answer</summary>

```text
True False
```

`math.nan` is a single float object, so it *is* itself. But nan's value is not equal to anything, even itself. This is the only common case where `x is x` is true but `x == x` is false.

</details>

### Common misconceptions

- "`is` is just a faster `==`." No. It answers a different question.
- "`a is b` is `True` for equal numbers." Only by accident of caching.

---

## Summary

- `print()` converts values with `str()`, joins them with `sep`, ends with `end`, writes to `file` (`sys.stderr` for errors) and returns `None`.
- `input()` always returns a `str`. Convert with `int()` or `float()`; bad text raises `ValueError`. Read the last traceback line first.
- Every value is an object with identity, type and value. Names are labels; assignment binds a label and never copies.
- Numbers, strings, bools and `None` are immutable.
- `int` has unlimited size. `//` floors, `%` follows the divisor's sign, and `(a // b) * b + a % b == a`. `int()` truncates.
- A float is a 64-bit IEEE 754 binary number (about 15 to 17 digits). `0.1 + 0.2 != 0.3`; `nan != nan`.
- `round()` rounds halves to even. Compare floats with `math.isclose()` (add `abs_tol` near zero).
- Use `Decimal("...")` with `quantize()` for money, and `Fraction` for exact ratios. `complex` uses `j`.
- `bool` is a subclass of `int`. Test `None` with `is`.
- Falsy: `False`, `None`, zeros, empty collections. `and`/`or` short-circuit and return an operand.
- `**` is right-associative and beats unary minus on its left. Comparisons chain.
- Numbers widen bool, int, float, complex automatically; strings never convert automatically.
- `+=` rebinds immutables; `:=` assigns inside expressions; `is` checks identity, `==` checks value.

## Learning outcomes

After this chapter you should be able to:

- [ ] Use `print()` with `sep`, `end` and `file=sys.stderr`, and explain what `flush` is for.
- [ ] Read numbers from the user safely with `int()` and `float()`, and recognise invalid input from a `ValueError` traceback.
- [ ] Describe identity, type and value; explain why assignment is not copying.
- [ ] Predict floor division and modulo with negative numbers, and contrast `//` with `int()` truncation.
- [ ] Explain why `0.1 + 0.2 != 0.3` and choose `decimal` for money.
- [ ] Predict `round()` results, including `round(2.5)` and `round(2.675, 2)`.
- [ ] Compare floats with `math.isclose()`, using `abs_tol` near zero.
- [ ] Use `Decimal` with `quantize()`, `ROUND_HALF_UP` and `getcontext().prec`, and `Fraction` for exact ratios.
- [ ] List the falsy values, predict what `and`/`or` return, and test with `is None`.
- [ ] Evaluate expressions using the precedence table, including `-2 ** 2`, `2 ** 3 ** 2` and chained comparisons.
- [ ] Apply the type conversion rules, and choose between `is` and `==`.

## Module project

The project for this module is a **unit converter and precise money calculator with input validation**. You will read values from the user, convert them to numbers, and produce clearly formatted results. Use floats with `math.isclose()` and sensible rounding for unit conversions (such as kilometres to miles, or Celsius to Fahrenheit). Use `Decimal` built from strings, with `quantize()` and an explicit rounding mode, for money (prices, tax, totals). Think about what each kind of bad text does to `int()`, `float()` and `Decimal()`, and be ready to explain every error message your program could show. The project brief gives the exact requirements.

## Further reading

All links are to the official Python documentation.

- print(): https://docs.python.org/3/library/functions.html#print
- input(): https://docs.python.org/3/library/functions.html#input
- Objects, values and types: https://docs.python.org/3/reference/datamodel.html#objects-values-and-types
- Numeric types (int, float, complex): https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex
- Floating-point arithmetic, issues and limitations: https://docs.python.org/3/tutorial/floatingpoint.html
- round(): https://docs.python.org/3/library/functions.html#round
- math.isclose(): https://docs.python.org/3/library/math.html#math.isclose
- decimal module: https://docs.python.org/3/library/decimal.html
- fractions module: https://docs.python.org/3/library/fractions.html
- Truth value testing: https://docs.python.org/3/library/stdtypes.html#truth-value-testing
- Operator precedence: https://docs.python.org/3/reference/expressions.html#operator-precedence
- Comparisons: https://docs.python.org/3/reference/expressions.html#comparisons
- Assignment expressions: https://docs.python.org/3/reference/expressions.html#assignment-expressions

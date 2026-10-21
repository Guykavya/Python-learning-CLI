# Chapter 3: Strings and text

Almost every program you will ever write touches text. Names, messages, file contents, web pages, log lines, passwords, CSV rows: all of them are strings. In the last chapter you met `str` as one of Python's basic types and used simple f-strings. In this chapter we take strings apart completely.

You will learn how to write any string literal you need, how to pull out any piece of a string with indexing and slicing, and how to use the large toolbox of string methods so you rarely need to write a loop for text work. You will learn the format specification mini-language that controls exactly how numbers appear in f-strings. Then we go below the surface: what a character really is (a Unicode code point), how text becomes bytes on disk (encoding, usually UTF-8), and how to fix the encoding errors that confuse so many beginners.

Run every example yourself. Answer every "Predict the output" question in your head, or on paper, before opening the answer. That habit is what turns reading into understanding.

A note on how examples are shown. A block of code is followed by the exact output it produces when run as a script with Python 3.14. When an example produces an error, the traceback path is shortened to `example.py`. When a string has spaces at its end, the example usually prints it between square brackets, like `[hi  ]`, so you can see the spaces.

A note on lists. Some string methods, such as `split()`, give back a **list**: a value written like `['a', 'b', 'c']` that holds several strings in order. In this chapter we only use lists in simple ways: print them, take their `len()`, index them like `words[0]`, and glue them back into a string with `join()`. Lists themselves are covered properly in core.05.

## Table of contents

1. [What a string is](#1-what-a-string-is)
2. [String literals and escape sequences](#2-string-literals-and-escape-sequences)
3. [Raw strings and multiline strings](#3-raw-strings-and-multiline-strings)
4. [str() and repr()](#4-str-and-repr)
5. [Indexing](#5-indexing)
6. [Slicing in depth](#6-slicing-in-depth)
7. [Operators on strings](#7-operators-on-strings)
8. [Immutability and efficient building](#8-immutability-and-efficient-building)
9. [Changing case](#9-changing-case)
10. [Searching: in, find, index, count, startswith, endswith](#10-searching-in-find-index-count-startswith-endswith)
11. [Cleaning: strip, removeprefix, removesuffix, replace](#11-cleaning-strip-removeprefix-removesuffix-replace)
12. [Splitting and joining](#12-splitting-and-joining)
13. [partition and rpartition](#13-partition-and-rpartition)
14. [Testing characters: the is methods](#14-testing-characters-the-is-methods)
15. [Padding: center, ljust, rjust, zfill](#15-padding-center-ljust-rjust-zfill)
16. [f-strings in depth](#16-f-strings-in-depth)
17. [The format specification mini-language](#17-the-format-specification-mini-language)
18. [Unicode, code points, ord and chr](#18-unicode-code-points-ord-and-chr)
19. [Encoding and decoding, UTF-8](#19-encoding-and-decoding-utf-8)
20. [Encoding errors and how to fix them](#20-encoding-errors-and-how-to-fix-them)
21. [bytes and bytearray](#21-bytes-and-bytearray)
22. [The string module](#22-the-string-module)
23. [The textwrap module](#23-the-textwrap-module)
24. [translate and maketrans](#24-translate-and-maketrans)
25. [Summary](#summary)
26. [Learning outcomes](#learning-outcomes)
27. [Module project](#module-project)
28. [Further reading](#further-reading)

---

## 1. What a string is

A **string** is an ordered sequence of characters. Its type is `str`. "Ordered" means each character has a position, and the order matters: `"stop"` and `"pots"` contain the same letters but are different strings.

```python
greeting = "Hello"
print(greeting)
print(type(greeting))
print(len(greeting))
print(len(""))
```

Output:

```text
Hello
<class 'str'>
5
0
```

`len()` counts the characters. The empty string `""` has length 0. It is still a perfectly good string, just with nothing in it.

Three facts shape everything else in this chapter:

1. **A string is a sequence.** You can ask for the character at a position (indexing), a piece of it (slicing), and its length.
2. **A string is immutable.** Once created, it can never change. Every method that seems to "change" a string actually builds and returns a *new* string.
3. **A character is a Unicode code point.** It is not a byte. The letter `é` and the emoji `🙂` each count as one character, even though they take more than one byte when saved to a file.

### Under the hood

Python has no separate "character" type. A single character is just a string of length 1. So `"Hello"[0]` gives you the string `"H"`, not some special char value. This keeps the language small: everything you learn about strings also works on single characters.

---

## 2. String literals and escape sequences

A **literal** is a value written directly in your code. A string literal is text inside quotes. Python accepts single quotes and double quotes, and they mean exactly the same thing.

```python
a = 'hello'
b = "hello"
print(a == b)
print('She said "yes"')
print("It's fine")
```

Output:

```text
True
She said "yes"
It's fine
```

The rule of thumb: pick the quote that does **not** appear inside the text. That avoids awkward escapes. Most Python code uses double quotes by default, and this book does too.

### Escape sequences

Some characters are hard or impossible to type inside quotes: a newline, a tab, or the same quote that surrounds the string. For these, Python uses **escape sequences**: a backslash `\` followed by a code.

| Escape | Meaning |
|---|---|
| `\n` | newline (move to the next line) |
| `\t` | tab |
| `\\` | one backslash |
| `\'` | single quote |
| `\"` | double quote |
| `\r` | carriage return |
| `\0` | the character with code 0 (null) |
| `\xhh` | the character with hex code hh, like `\x41` for `A` |
| `\uhhhh` | the character with 4-digit hex code, like `\u00e9` for `é` |
| `\Uhhhhhhhh` | the character with 8-digit hex code, like `\U0001F642` for `🙂` |
| `\N{name}` | the character with this Unicode name, like `\N{BULLET}` |

```python
print("Line one\nLine two")
print("Name:\tAsha")
print("A backslash: \\")
print('It\'s here')
print("Quote: \"hi\"")
print("\x41\u00e9\U0001F642")
print("\N{BULLET} item")
print(len("a\nb"))
```

Output:

```text
Line one
Line two
Name:	Asha
A backslash: \
It's here
Quote: "hi"
Aé🙂
• item
3
```

Look at the last line. `"a\nb"` is written with four symbols in the source code, but the string has only **3** characters: `a`, a newline, and `b`. The escape sequence `\n` is how you *write* one character; it is not two characters in the string.

### Under the hood

Escapes are handled by the Python compiler when it reads your source file, before your program runs. By the time your code executes, the string simply contains a newline character. Nothing at run time knows that you typed `\n`.

### Unknown escapes

If a backslash is followed by something that is not a known escape, such as `\d`, Python keeps both characters, but it also prints a `SyntaxWarning`, because this is usually a mistake (often a Windows path or a regular expression). Future versions of Python will make it an error. The fix is a raw string, which comes next.

### Predict the output

```python
print(len("\t"))
print(len("\\n"))
print("a\\tb")
print("C:\\new")
```

<details><summary>Answer</summary>

```text
1
2
a\tb
C:\new
```

- `"\t"` is one tab character, so length 1.
- `"\\n"` is a backslash followed by the letter n: two characters.
- `"a\\tb"` prints `a\tb` literally, because `\\` is one backslash and then `t` is an ordinary letter.
- `"C:\\new"` prints `C:\new`.

</details>

### Common misconceptions

- "`\n` is two characters." In the source code you type two symbols, but the string holds one character.
- "Single quotes are for characters, double quotes for strings." That is true in C and Java, not in Python. They are identical.
- "`print` adds the quotes." `print` shows the string's content without quotes. The quotes are only part of the literal.

---

## 3. Raw strings and multiline strings

### Raw strings

Put an `r` in front of a literal and backslashes lose their special meaning. Every backslash stays a backslash. This is called a **raw string**.

```python
print("C:\new\table")
print(r"C:\new\table")
print(len(r"\n"))
```

Output:

```text
C:
ew	able
C:\new\table
2
```

The first line went wrong: `\n` became a newline and `\t` became a tab. The raw version prints exactly what you typed. Raw strings are used for Windows paths and, in core.04, for regular expressions, which are full of backslashes.

One odd rule: a raw string cannot end with an odd number of backslashes. `r"C:\"` is a syntax error, because the backslash still stops the quote from closing the string. Write `"C:\\"` instead, or use forward slashes, which Windows also accepts.

### Multiline strings

Three quotes in a row (`"""` or `'''`) start a **triple-quoted string**. It can span several lines, and the line breaks become real newline characters in the string.

```python
poem = """Roses are red,
Violets are blue."""
print(poem)
print(len(poem.splitlines()))
```

Output:

```text
Roses are red,
Violets are blue.
2
```

Watch out for the first and last line. If you start the text on the line after the opening quotes, the string begins with a newline. A backslash at the very end of a line inside the literal joins the lines and removes that newline:

```python
a = """
hello
"""
b = """\
hello
"""
print(repr(a))
print(repr(b))
```

Output:

```text
'\nhello\n'
'hello\n'
```

(`repr()` shows a string with quotes and escapes, so you can see invisible characters. It is explained in the next section.)

Triple-quoted strings are also used for **docstrings**, the descriptions written at the top of modules and functions. You will write those from core.06.

### Implicit concatenation

Two string literals written side by side, with only spaces or line breaks between them, are joined into one by the compiler. Inside brackets this lets you split a long string over several lines:

```python
message = ("This is a long message "
           "that continues here "
           "and ends here.")
print(message)
print("ab" "cd")
```

Output:

```text
This is a long message that continues here and ends here.
abcd
```

This only works for **literals**. Two variables next to each other, like `a b`, are a syntax error.

### Common misconceptions

- "Raw strings are a different type." No. `r"\n"` is an ordinary `str` of length 2. The `r` only changes how the literal is read.
- "Triple quotes are comments." A triple-quoted string on its own line is just a string that nobody uses. Python ignores it, so it looks like a comment, but real comments start with `#`.

---

## 4. str() and repr()

Every object has two text forms:

- `str(x)` is the **friendly** form, meant for users. `print()` uses it.
- `repr(x)` is the **developer** form, meant to be unambiguous. For strings it adds quotes and shows escapes.

```python
s = "Tab\there\n"
print(str(s))
print(repr(s))
print(repr("it's"))
print(repr('say "hi"'))
print(repr(42), repr(3.0))
```

Output:

```text
Tab	here

'Tab\there\n'
"it's"
'say "hi"'
42 3.0
```

When you are debugging text, `repr()` is your best friend. It shows trailing spaces, tabs and newlines that `print()` hides. In an f-string, `{x!r}` gives the repr (see section 16).

```python
name = "Asha  "
print("Name is", name, "!")
print("Name is", repr(name), "!")
```

Output:

```text
Name is Asha   !
Name is 'Asha  ' !
```

---

## 5. Indexing

Each character in a string has a position number called an **index**. Counting starts at **0**, not 1. You read one character with square brackets: `s[i]`.

```
 P   y   t   h   o   n
 0   1   2   3   4   5     positive index
-6  -5  -4  -3  -2  -1     negative index
```

**Negative indices** count from the end. `-1` is the last character, `-2` the one before it. Python simply adds the length: `s[-1]` means `s[len(s) - 1]`.

```python
s = "Python"
print(s[0])
print(s[5])
print(s[-1])
print(s[-6])
print(s[len(s) - 1])
```

Output:

```text
P
n
n
P
n
```

### Out of range

An index that does not exist raises an `IndexError`:

```python
s = "Python"
print(s[6])  # error expected
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    print(s[6])  # error expected
          ~^^^
IndexError: string index out of range
```

Valid indices for a string of length `n` run from `0` to `n - 1`, and from `-1` to `-n`. An empty string has no valid index at all, so `""[0]` is an error too. Remember that when a user might type nothing.

### Under the hood

A Python string stores its characters in a compact array where every character uses the same number of bytes (1, 2 or 4, chosen by the widest character in the string). Because every slot is the same size, finding character number `i` is a single multiplication, no matter how long the string is. That is why indexing is fast (constant time).

### Predict the output

```python
word = "banana"
print(word[1], word[-2], word[len(word) // 2])
print(word[0] == word[-1])
print("🙂ok"[1])
```

<details><summary>Answer</summary>

```text
a n a
False
o
```

- `word[1]` is `a`, `word[-2]` is `n`, `word[6 // 2]` is `word[3]`, which is `a`.
- First is `b`, last is `a`, so `False`.
- The emoji is one character, so index 1 is `o`.

</details>

### Common misconceptions

- "The last index is `len(s)`." It is `len(s) - 1`. Using `len(s)` is the classic off-by-one error.
- "`s[-0]` is the last character." `-0` is just `0`, the first character.

---

## 6. Slicing in depth

A **slice** pulls out a piece of a string. The full form is `s[start:stop:step]`.

- `start` is the index of the first character you want (included).
- `stop` is the index where you stop (**not** included).
- `step` is how far to jump each time (default 1).

The "stop is excluded" rule feels strange at first, but it has lovely results: `s[a:b]` has exactly `b - a` characters, and `s[:k] + s[k:]` is always the whole string.

The best mental picture is to number the **gaps between** characters, not the characters themselves:

```
  | P | y | t | h | o | n |
  0   1   2   3   4   5   6
 -6  -5  -4  -3  -2  -1
```

`s[1:4]` is everything between gap 1 and gap 4: `yth`.

```python
s = "Python"
print(s[1:4])
print(s[:2])
print(s[2:])
print(s[:])
print(s[-3:])
print(s[:-1])
print(s[1:-1])
print(s[:3] + s[3:])
```

Output:

```text
yth
Py
thon
Python
hon
Pytho
ytho
Python
```

### Defaults

Any of the three parts can be left out:

- Missing `start` means "from the beginning" (or from the end when the step is negative).
- Missing `stop` means "to the end" (or to the beginning when the step is negative).
- Missing `step` means 1.

So `s[:]` is a copy of the whole string, `s[:3]` is the first three characters, `s[-3:]` is the last three, and `s[:-1]` drops the last character.

### Out-of-range slices never fail

This is the big difference from indexing. A slice quietly trims its bounds to fit the string. It never raises an error; at worst it gives an empty string.

```python
s = "Python"
print(repr(s[2:100]))
print(repr(s[-100:2]))
print(repr(s[10:20]))
print(repr(s[4:2]))
print(repr(""[0:5]))
```

Output:

```text
'thon'
'Py'
''
''
''
```

`s[4:2]` is empty because, with a positive step, you cannot walk forward from 4 and reach 2. This "never fails" rule is useful: `s[:20]` safely takes "at most 20 characters" from any string, even a short or empty one.

### Steps

The step picks every second, third, or n-th character:

```python
digits = "0123456789"
print(digits[::2])
print(digits[1::2])
print(digits[::3])
print(digits[2:8:2])
```

Output:

```text
02468
13579
0369
246
```

### Negative steps

A negative step walks **backwards**. Now `start` should be to the right of `stop`.

```python
s = "Python"
print(s[::-1])
print(s[::-2])
print(s[4:1:-1])
print(s[-1:-4:-1])
print(repr(s[1:4:-1]))
```

Output:

```text
nohtyP
nhy
oht
noh
''
```

`s[::-1]` is the standard way to reverse a string. `s[4:1:-1]` starts at index 4 (`o`), walks left, and stops before index 1: `oht`. The last one is empty: starting at 1 and walking left you can never reach 4.

A step of 0 is not allowed:

```python
print("abc"[::0])  # error expected
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    print("abc"[::0])  # error expected
          ~~~~~^^^^^
ValueError: slice step cannot be zero
```

### Slices make new strings

A slice always builds a new string. The original is untouched (strings are immutable, after all).

### Under the hood

Python turns `start:stop:step` into a `slice` object and normalises it: negative numbers get `len(s)` added, then values are clipped into range. You can make one yourself, which is handy for naming a slice you use often:

```python
year = slice(0, 4)
date = "2026-10-18"
print(date[year])
print(slice(1, 4).indices(3))
```

Output:

```text
2026
(1, 3, 1)
```

`indices(3)` shows the clipped `(start, stop, step)` Python really uses for a length-3 string: the stop of 4 was trimmed to 3.

### Predict the output

```python
s = "abcdefgh"
print(s[2:5])
print(s[-3:-1])
print(s[::-3])
print(s[5:2:-1])
print(repr(s[3:3]))
print(s[-100:3])
print(s[::-1][:3])
```

<details><summary>Answer</summary>

```text
cde
fg
heb
fed
''
abc
hgf
```

- `s[2:5]` is indices 2, 3, 4: `cde`.
- `s[-3:-1]` is indices 5 and 6: `fg` (the stop, index 7, is excluded).
- `s[::-3]` starts at the last character `h`, then `e`, then `b`.
- `s[5:2:-1]` is indices 5, 4, 3: `fed`.
- `s[3:3]` is empty: start equals stop.
- `s[-100:3]` clips the start to 0: `abc`.
- Reverse first (`hgfedcba`) and take three: `hgf`.

</details>

### Common misconceptions

- "`s[2:5]` includes index 5." It does not. The stop is always excluded.
- "`s[-1:]` and `s[:-1]` are the same." The first is the last character; the second is everything except the last character.
- "A negative step reverses the given range." `s[1:4:-1]` is not `s[1:4]` reversed; it is empty. To reverse a range, write `s[1:4][::-1]` or `s[3:0:-1]`.
- "Slicing past the end is an error." Only indexing is. Slices clip silently.

### Edge cases

- `""[::-1]` is `""`. Reversing an empty string is fine.
- `s[:0]` is always `""`, and `s[len(s):]` is always `""`.
- For any `k`, `s[:k] + s[k:] == s`, even when `k` is negative or out of range.


---

## 7. Operators on strings

Several operators you know from numbers also work on strings, with different meanings.

```python
print("snow" + "ball")
print("ha" * 3)
print(3 * "-")
print("-" * 0)
print("an" in "banana")
print("x" not in "banana")
print("" in "banana")
```

Output:

```text
snowball
hahaha
---

True
True
True
```

- `+` **concatenates** (joins) two strings. Both sides must be strings.
- `*` with an integer **repeats** a string. Zero or a negative number gives `""`.
- `in` tests whether one string appears **anywhere** inside another as a substring. The empty string is inside every string.

Mixing a string and a number with `+` is an error. Python never converts silently:

```python
age = 20
print("Age: " + age)  # error expected
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    print("Age: " + age)  # error expected
          ~~~~~~~~^~~~~
TypeError: can only concatenate str (not "int") to str
```

Fix it with `str(age)`, or better, with an f-string: `f"Age: {age}"`.

### Comparing strings

`==` and `!=` compare content, character by character. `<`, `>` and friends compare **lexicographically**, like a dictionary, but using each character's code point number (section 18), not the alphabet you learnt at school.

```python
print("apple" < "banana")
print("apple" < "apricot")
print("app" < "apple")
print("Zebra" < "apple")
print("10" < "9")
print(min("pear", "fig", "apple"), max("pear", "fig", "apple"))
```

Output:

```text
True
True
True
True
True
apple pear
```

Two surprises live here. Every uppercase ASCII letter (codes 65 to 90) comes before every lowercase one (97 to 122), so `"Zebra" < "apple"`. And digit strings are compared as text, so `"10" < "9"` because `"1"` comes before `"9"`. Convert to `int` if you mean numbers. To compare text without caring about case, compare `a.casefold() < b.casefold()`.

### Under the hood

`len(s)` is instant: the length is stored inside the string object. `in` scans the string; CPython uses a clever search algorithm that is usually very fast, but in the worst case its time grows with the length of the text.

---

## 8. Immutability and efficient building

A string can never be changed after it is created. You cannot assign to an index:

```python
s = "cat"
s[0] = "b"  # error expected
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    s[0] = "b"  # error expected
    ~^^^
TypeError: 'str' object does not support item assignment
```

To "change" a string, you build a new one and, usually, rebind the name to it:

```python
s = "cat"
s = "b" + s[1:]
print(s)
```

Output:

```text
bat
```

Every string method works the same way: it **returns a new string** and leaves the original alone. This is the source of one of the most common beginner bugs:

```python
name = "asha"
name.upper()
print(name)
name = name.upper()
print(name)
```

Output:

```text
asha
ASHA
```

The first call built `"ASHA"` and threw it away, because nothing kept it. You must store the result.

### Why immutable?

- **Safety.** If you pass a string to some code, that code cannot change your copy behind your back.
- **Sharing.** Because no one can change it, Python can safely let many names point at the same string object.
- **Hashing.** Immutable values can be used as dictionary keys (core.05), because their hash never changes.

### Building strings efficiently

Because every `+` creates a brand-new string and copies both pieces into it, building a long string by adding a little at a time does a lot of copying. If you add 1,000 small pieces one by one, the program copies the growing string again and again. In the worst case the total work grows with the *square* of the number of pieces.

The efficient tool is `str.join()`. You give it all the pieces at once; it works out the final length, makes one string of that size, and copies each piece in exactly once.

```python
parts = ["2026", "10", "18"]
print("-".join(parts))
print("".join(["a", "b", "c"]))
print(", ".join("xyz"))
```

Output:

```text
2026-10-18
abc
x, y, z
```

`join` is called on the **separator** and takes the pieces as its argument. Any sequence of strings works, including a string itself, whose pieces are its characters. You will use `join` with loops and lists from core.05 onwards. For now, remember the rule:

> To build text from many pieces, collect the pieces and `join` them once. Do not grow a string with `+=` inside a loop.

### Under the hood

CPython has a hidden optimisation: when you write `s += t` and nothing else refers to `s`, it can sometimes grow the string in place instead of copying. This is why `+=` in a loop is not always slow when you test it. But the optimisation is fragile (one extra name pointing at `s` turns it off) and other Python implementations do not have it. `join` is fast everywhere.

### Predict the output

```python
s = "hello"
t = s
s = s.replace("h", "j")
print(s, t)
word = "abc"
word.upper()
print(word)
print("+".join("123"))
```

<details><summary>Answer</summary>

```text
jello hello
abc
1+2+3
```

- `replace` built a new string `"jello"` and `s` was rebound to it. `t` still names the old `"hello"`.
- `word.upper()`'s result was thrown away, so `word` is still `abc`.
- `join` puts `+` between the characters: `1+2+3`.

</details>

### Common misconceptions

- "Methods change the string." No string method ever changes the string. They all return new ones.
- "`s += 'x'` changes `s`." It builds a new string and rebinds the name `s`. Other names still see the old string.
- "`join` takes the separator as its argument." It is the other way round: `separator.join(pieces)`.

---

## 9. Changing case

| Method | What it does | `"hello WORLD"` becomes |
|---|---|---|
| `upper()` | all letters uppercase | `HELLO WORLD` |
| `lower()` | all letters lowercase | `hello world` |
| `title()` | first letter of each word uppercase, rest lowercase | `Hello World` |
| `capitalize()` | first character uppercase, rest lowercase | `Hello world` |
| `swapcase()` | flip each letter's case | `HELLO world` |
| `casefold()` | aggressive lowercase, for comparing | `hello world` |

```python
s = "hello WORLD"
print(s.upper(), s.lower(), s.title(), s.capitalize(), s.swapcase(), sep=" / ")
```

Output:

```text
HELLO WORLD / hello world / Hello World / Hello world / HELLO world
```

Characters that are not letters, like digits and punctuation, are left alone.

### casefold versus lower

For English, `lower()` and `casefold()` give the same result. For some languages they differ. The German letter `ß` lowercases to itself, but casefolds to `ss`, because Germans treat `Straße` and `STRASSE` as the same word.

```python
print("Straße".lower())
print("Straße".casefold())
print("STRASSE".lower() == "Straße".lower())
print("STRASSE".casefold() == "Straße".casefold())
print("ß".upper(), len("ß".upper()))
```

Output:

```text
straße
strasse
False
True
SS 2
```

Notice the last line: `upper()` turned one character into two. Case changes can change a string's length. The rule: use `lower()` or `upper()` to *display* text, and `casefold()` to *compare* text without caring about case.

### title() has a known weakness

`title()` starts a new "word" after any character that is not a letter. That includes apostrophes:

```python
print("they're o'neil's friends".title())
```

Output:

```text
They'Re O'Neil'S Friends
```

`They'Re` is wrong. For simple word-by-word capitalisation, `string.capwords()` (section 22) splits on spaces instead, so `they're` correctly becomes `They're`. (No simple method knows that O'Neil needs a capital N; names are genuinely hard.)

### Common misconceptions

- "`lower()` is fine for case-insensitive comparison." Usually, but not always. `casefold()` is designed for it.
- "Case methods keep the length." `"ß".upper()` is `"SS"`.

---

## 10. Searching: in, find, index, count, startswith, endswith

### in

`sub in s` answers yes or no: does `sub` appear in `s`? When you only need yes or no, use `in`. It is the clearest.

### find and rfind

`s.find(sub)` returns the index where `sub` **first** starts, or **-1** if it is not there. `s.rfind(sub)` searches from the right and returns the index of the **last** occurrence (still counted from the left).

```python
s = "banana"
print(s.find("an"))
print(s.rfind("an"))
print(s.find("x"))
print(s.find("a", 2))
print(s.find("a", 2, 3))
```

Output:

```text
1
3
-1
3
-1
```

The optional second and third arguments are `start` and `end`, like a slice: search only within `s[start:end]`. The returned index is still counted from the beginning of `s`.

### The -1 trap

`-1` is a valid index in Python: it means the last character. If you use the result of `find` without checking it, a "not found" quietly turns into "the last character":

```python
s = "hello"
pos = s.find("z")
print(pos, s[pos])
```

Output:

```text
-1 o
```

No error, wrong answer. That is the worst kind of bug.

### index and rindex

`s.index(sub)` is like `find`, except that when `sub` is missing it raises `ValueError` instead of returning -1. Use `index` when the text *must* be there and a missing value is a real error you want to hear about. `rindex` is the right-hand version.

```python
print("banana".index("n"))
print("banana".index("z"))  # error expected
```

Output:

```text
2
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    print("banana".index("z"))  # error expected
          ~~~~~~~~~~~~~~^^^^^
ValueError: substring not found
```

### count

`s.count(sub)` counts **non-overlapping** occurrences, scanning from left to right. Once a match is found, the search continues after it.

```python
print("banana".count("a"))
print("banana".count("ana"))
print("aaaa".count("aa"))
print("hello".count(""))
```

Output:

```text
3
1
2
6
```

`"banana"` contains `ana` at index 1 and index 3, but those overlap (they share the `a` at index 3), so `count` finds only one. `"aaaa".count("aa")` is 2, not 3, for the same reason. Counting the empty string gives `len(s) + 1`: there is an empty string at every gap.

### startswith and endswith

```python
url = "https://example.com/photo.PNG"
print(url.startswith("https://"))
print(url.endswith(".png"))
print(url.lower().endswith(".png"))
print(url.endswith((".jpg", ".png", ".PNG")))
```

Output:

```text
True
False
True
True
```

Both accept a **tuple** of options (values in round brackets separated by commas) and return `True` if any of them matches. They are clearer and safer than slicing: `s[:8] == "https://"` breaks the moment you miscount the length.

### Under the hood

All of these return information about the string; none changes it. They all do case-sensitive matching. Lowercase or casefold both sides first if you need case-insensitive searching.

### Predict the output

```python
s = "mississippi"
print(s.find("ss"), s.rfind("ss"))
print(s.count("ss"), s.count("issi"))
print(s.find("i", 5), s.find("Miss"))
print(s.startswith("miss"), s.endswith(("pi", "zz")))
print(s[s.find("q")])
```

<details><summary>Answer</summary>

```text
2 5
2 1
7 -1
True True
i
```

- `ss` starts at 2, and last at 5.
- `ss` appears twice. `issi` appears at 1 and at 4, but they overlap at index 4, so `count` gives 1.
- From index 5, the next `i` is at 7. `"Miss"` with a capital M is not there: -1.
- Both true (`pi` matches at the end).
- `find` returns -1, so this prints the last character, `i`. No error, which is exactly the trap.

</details>

### Common misconceptions

- "`find` returns `False` or `None` when nothing is found." It returns -1, which is a valid index.
- "`count` counts overlapping matches." It does not.
- "`s.find(x) > 0` means found." Index 0 is a real match. Use `s.find(x) != -1`, or simply `x in s`.

---

## 11. Cleaning: strip, removeprefix, removesuffix, replace

### The strip family

`strip()` removes whitespace (spaces, tabs, newlines) from **both ends**. `lstrip()` removes from the left only, `rstrip()` from the right only. Whitespace in the middle is never touched.

```python
raw = "   Asha Kumar \t\n"
print(repr(raw.strip()))
print(repr(raw.lstrip()))
print(repr(raw.rstrip()))
```

Output:

```text
'Asha Kumar'
'Asha Kumar \t\n'
'   Asha Kumar'
```

You can pass the characters to remove. This argument is a **set of characters**, not a word. Python keeps removing from each end while the end character is anywhere in that set.

```python
print("xxhixyx".strip("x"))
print("www.compass.com".strip("w.moc"))
print("--==title==--".strip("=-"))
```

Output:

```text
hixy
pass
title
```

The second line surprises people. Someone hoping to get `compass` gets `pass`. From the left, `strip("w.moc")` removed `w`, `w`, `w`, `.`, `c`, `o` and `m`, because every one of them is in the set, and stopped at `p`. From the right it removed `m`, `o`, `c` and `.`, and stopped at `s`.

### removeprefix and removesuffix

When you want to remove one exact piece of text from one end, use `removeprefix()` or `removesuffix()` (added in Python 3.9). They remove the text once, and only if it is really there.

```python
print("www.example.com".removeprefix("www.").removesuffix(".com"))
print("report.txt".removesuffix(".csv"))
print("##tag".removeprefix("#"))
print("##tag".lstrip("#"))
```

Output:

```text
example
report.txt
#tag
tag
```

Compare the last two lines. `removeprefix("#")` removed one `#`. `lstrip("#")` removed every `#` from the left.

### replace

`s.replace(old, new)` returns a copy with every occurrence of `old` replaced by `new`. An optional third argument limits how many replacements are made, starting from the left.

```python
s = "one fish two fish"
print(s.replace("fish", "cat"))
print(s.replace("fish", "cat", 1))
print(s.replace(" ", ""))
print(s.replace("FISH", "cat"))
print("aaa".replace("a", "aa"))
```

Output:

```text
one cat two cat
one cat two fish
onefishtwofish
one fish two fish
aaaaaa
```

`replace` is case-sensitive, and it scans the original string, so the new text is never searched again. That is why `"aaa".replace("a", "aa")` does not loop forever.

### Common misconceptions

- "`strip("abc")` removes the word abc." It removes any of the characters a, b and c from both ends.
- "`strip()` removes all spaces." Only at the ends. Use `replace(" ", "")` to remove every space, or `" ".join(s.split())` to collapse runs of spaces (next section).
- "`replace` changes the string in place." It returns a new one.

---

## 12. Splitting and joining

### split()

`s.split(sep)` cuts a string at every `sep` and returns the pieces as a list.

```python
print("a,b,c".split(","))
print("a,,b".split(","))
print(",a,".split(","))
print("2026-10-18".split("-"))
```

Output:

```text
['a', 'b', 'c']
['a', '', 'b']
['', 'a', '']
['2026', '10', '18']
```

With an explicit separator, every separator makes a cut, so two separators in a row give an empty piece, and a separator at an end gives an empty piece at that end. That is exactly what you want for formats like CSV where empty fields matter.

### split() with no argument

Called with no argument, `split()` uses a completely different rule. It splits on **runs of any whitespace** and ignores whitespace at the ends. You never get empty pieces.

```python
s = "  the   quick\tbrown \n fox  "
print(s.split())
print(s.split(" "))
print("".split())
print("".split(","))
print(len("  hello   world ".split()))
```

Output:

```text
['the', 'quick', 'brown', 'fox']
['', '', 'the', '', '', 'quick\tbrown', '\n', 'fox', '', '']
[]
['']
2
```

Look carefully at the two empty-string cases. `"".split()` is an empty list (there are no words), but `"".split(",")` is a list holding one empty string (one empty field). This difference matters when you count words versus fields.

A handy idiom: `" ".join(s.split())` collapses all runs of whitespace into single spaces and trims both ends.

```python
messy = "  too    many   spaces  "
print("[" + " ".join(messy.split()) + "]")
```

Output:

```text
[too many spaces]
```

### maxsplit and rsplit

The `maxsplit` argument limits how many cuts are made. `rsplit()` makes its cuts starting from the right. They only differ when `maxsplit` is used.

```python
path = "home/asha/docs/notes.txt"
print(path.split("/", 1))
print(path.rsplit("/", 1))
print("k=v=w".split("=", maxsplit=1))
```

Output:

```text
['home', 'asha/docs/notes.txt']
['home/asha/docs', 'notes.txt']
['k', 'v=w']
```

`rsplit("/", 1)` is the classic way to separate a folder from a file name.

### splitlines

`splitlines()` splits at line breaks. Unlike `split("\n")`, it understands Windows line endings (`\r\n`) and does not give an empty last piece when the text ends with a newline.

```python
text = "first\r\nsecond\nthird\n"
print(text.split("\n"))
print(text.splitlines())
print(text.splitlines(keepends=True))
```

Output:

```text
['first\r', 'second', 'third', '']
['first', 'second', 'third']
['first\r\n', 'second\n', 'third\n']
```

Use `splitlines()` whenever you split text into lines.

### Working with the resulting list

For now, you can do these things with the list `split` gives you: print it, take `len()`, index it, slice it, and `join` it.

```python
words = "the quick brown fox".split()
print(len(words))
print(words[0], words[-1])
print(words[1:3])
print(" ".join(words[::-1]))
print("-".join(words).upper())
```

Output:

```text
4
the fox
['quick', 'brown']
fox brown quick the
THE-QUICK-BROWN-FOX
```

### Under the hood

`split()` builds a new string for every piece. On a very large text that is a lot of objects. `partition()` (next section) is cheaper when you need only one cut.

### Predict the output

```python
print(len("a b  c".split(" ")))
print(len("a b  c".split()))
print("x--y--z".split("--"))
print("1.2.3.4".rsplit(".", 2))
print(len("one\ntwo\n".splitlines()))
print("|".join("a b c".split()))
```

<details><summary>Answer</summary>

```text
4
3
['x', 'y', 'z']
['1.2', '3', '4']
2
a|b|c
```

- Splitting on single spaces, the double space gives an empty piece: `['a', 'b', '', 'c']`, length 4.
- No-argument split ignores runs: three words.
- The separator can be several characters long.
- From the right, two cuts: `['1.2', '3', '4']`.
- Two lines; the final newline does not create a third.
- `a|b|c`.

</details>

### Common misconceptions

- "`split()` and `split(" ")` are the same." They differ on repeated, leading and trailing spaces, and on the empty string.
- "`split` changes the string into a list." It returns a new list; the string is unchanged.

---

## 13. partition and rpartition

`s.partition(sep)` cuts the string at the **first** `sep` and always returns exactly three parts: the text before, the separator itself, and the text after. If `sep` is not found, you get the whole string, then two empty strings.

```python
print("key=value=more".partition("="))
print("no separator".partition("="))
print("archive.tar.gz".rpartition("."))
print("noext".rpartition("."))
```

Output:

```text
('key', '=', 'value=more')
('no separator', '', '')
('archive.tar', '.', 'gz')
('', '', 'noext')
```

`rpartition` cuts at the **last** separator. If it is not found, the whole string comes **last**, with two empty strings before it.

Because the result always has three parts, you can unpack it into three names in one line. This is called **tuple unpacking**:

```python
user, at, domain = "asha@example.com".partition("@")
print(user)
print(domain)
print(repr(at))
```

Output:

```text
asha
example.com
'@'
```

The middle part tells you whether the separator was found: it is the separator, or `""`. Since `""` is falsy, you can combine it with `and` and `or` (from core.02) to choose a value without an `if`:

```python
name, dot, ext = "README".rpartition(".")
print(repr(dot and ext))
print((dot and ext) or "(no extension)")
```

Output:

```text
''
(no extension)
```

`dot and ext` gives `dot` (the empty string) when there is no dot, and `ext` otherwise. Then `or` replaces an empty result with a default.

### partition versus split

| Need | Use |
|---|---|
| Cut once at the first separator, safely | `partition` |
| Cut once at the last separator | `rpartition` |
| Cut at every separator | `split` |
| Cut by whitespace into words | `split()` with no argument |

`partition` never fails and never surprises you with the wrong number of parts.


---

## 14. Testing characters: the is methods

A family of methods answers questions about **every** character in a string. Each returns `True` only if the string is **not empty** and **all** its characters pass the test.

| Method | True when every character is |
|---|---|
| `isalpha()` | a letter (any language) |
| `isdigit()` | a digit, including superscripts like `²` |
| `isdecimal()` | a decimal digit 0 to 9 (any script), the strictest |
| `isnumeric()` | anything numeric, including `½` and Roman numeral characters |
| `isalnum()` | a letter or a numeric character |
| `isspace()` | whitespace |
| `isupper()` / `islower()` | cased characters are all upper / all lower (and there is at least one) |
| `istitle()` | title case, like `Hello World` |
| `isascii()` | in the ASCII range (this one is `True` for `""`) |
| `isidentifier()` | a valid Python name |

```python
print("abc".isalpha(), "abc1".isalpha(), "café".isalpha())
print("123".isdigit(), "-5".isdigit(), "3.5".isdigit(), "".isdigit())
print("²".isdigit(), "²".isdecimal(), "½".isnumeric(), "½".isdigit())
print("   ".isspace(), "".isspace())
print("ABC1".isupper(), "123".isupper())
print("my_var".isidentifier(), "2nd".isidentifier())
print("".isascii(), "café".isascii())
```

Output:

```text
True False True
True False False False
True False True False
True False
True False
True False
True False
```

### Important consequences

- `"-5".isdigit()` and `"3.5".isdigit()` are `False`. These methods test characters, not "is this a number". `int("-5")` works fine though.
- `"²".isdigit()` is `True`, but `int("²")` fails. If you plan to call `int()`, `isdecimal()` is the safer test.
- The empty string is `False` for almost all of them. Remember this when the user presses Enter without typing.
- `isupper()` ignores characters with no case, but needs at least one cased character: `"ABC1".isupper()` is `True` while `"123".isupper()` is `False`.

### Common misconceptions

- "`isdigit()` checks whether text can become an int." It does not handle signs, and it accepts characters `int()` rejects.
- "`isalpha()` means A to Z." It accepts letters from every language, like `é` and `अ`.

---

## 15. Padding: center, ljust, rjust, zfill

These methods pad a string to a given **width** with a fill character (a space by default). If the string is already that wide or wider, it is returned unchanged; they never cut text.

```python
w = "hi"
print("[" + w.ljust(6) + "]")
print("[" + w.rjust(6) + "]")
print("[" + w.center(6) + "]")
print("[" + w.center(7, "*") + "]")
print("[" + "toolong".rjust(3) + "]")
print("42".zfill(5), "-42".zfill(5), "+7".zfill(4))
```

Output:

```text
[hi    ]
[    hi]
[  hi  ]
[***hi**]
[toolong]
00042 -0042 +007
```

- `ljust` puts the text on the left (padding on the right). `rjust` puts it on the right.
- `center` splits the padding. When it cannot split evenly, the extra space goes to one side.
- `zfill` pads with zeros on the left and is sign-aware: the sign stays in front.
- The fill must be exactly one character.

The same effects, plus much more, are available in f-strings, which we turn to now. In new code, f-strings are usually clearer. The methods are still useful when the width or fill is already in a variable and you want a simple call.

---

## 16. f-strings in depth

An **f-string** is a string literal with `f` in front. Inside it, anything in curly braces `{}` is a Python expression. It is evaluated, converted to text, and inserted.

```python
name = "Asha"
marks = 87
print(f"{name} scored {marks} marks")
print(f"Next year: {2026 + 1}")
print(f"{name.upper()} has {len(name)} letters")
print(f"{marks / 100}")
```

Output:

```text
Asha scored 87 marks
Next year: 2027
ASHA has 4 letters
0.87
```

Any expression works: arithmetic, method calls, indexing, function calls. Keep them short; long logic inside braces is hard to read.

### Literal braces

To print a real brace, double it:

```python
x = 5
print(f"{{x}} is {x}")
```

Output:

```text
{x} is 5
```

### Conversions: !r, !s, !a

After the expression you can add `!r` to use `repr()` instead of `str()`, or `!a` for `ascii()`, which escapes every non-ASCII character.

```python
word = "café "
print(f"[{word}]")
print(f"[{word!r}]")
print(f"[{word!a}]")
```

Output:

```text
[café ]
['café ']
['caf\xe9 ']
```

`!r` is ideal in error messages and debugging output, because it makes spaces and empty strings visible.

### The = specifier for debugging

Write `=` after an expression and the f-string prints the expression's text, an equals sign, and the value (as `repr` by default). It saves you from typing the variable name twice when debugging.

```python
city = "Pune"
temp = 31.456
print(f"{city=}")
print(f"{temp=:.1f}")
print(f"{temp * 2 = }")
```

Output:

```text
city='Pune'
temp=31.5
temp * 2 = 62.912
```

Spaces around `=` are kept in the output. A format spec after `=` (like `:.1f`) applies to the value.

### Quotes inside f-strings

Since Python 3.12, you can reuse the same quote type inside the braces. In older versions you must use the other kind of quote. Using the other kind always works, so it is the more portable habit:

```python
d = "2026-10-18"
print(f"Year {d.split('-')[0]}")
```

Output:

```text
Year 2026
```

### Under the hood

An f-string is not a string stored in your program; it is compiled into code that evaluates each expression and joins the pieces. That is why the expressions see your variables, and why an f-string is evaluated afresh every time that line runs.

### Predict the output

```python
a, b = 7, 2
print(f"{a}/{b} = {a / b}")
print(f"{a // b=}")
print(f"{{{a}}}")
print(f"{'hi'!r} and {'hi'}")
```

<details><summary>Answer</summary>

```text
7/2 = 3.5
a // b=3
{7}
'hi' and hi
```

- `7/2 = 3.5`.
- The `=` form prints the expression text: `a // b=3`.
- `{{` gives a literal `{`, then `{a}` gives 7, then `}}` gives `}`: `{7}`.
- `!r` adds quotes: `'hi' and hi`.

</details>

---

## 17. The format specification mini-language

After a colon inside the braces comes a **format spec**: a short code that controls how the value is shown. The same codes work in `format(value, spec)` and in the older `str.format()` method.

The full shape is:

```
[[fill]align][sign][z][#][0][width][grouping][.precision][type]
```

That looks dense, but each part is optional, and you will mostly use two or three at a time. We go through them in order of usefulness.

### Width and alignment

`width` is the **minimum** number of characters. Alignment is `<` (left), `>` (right) or `^` (centre). Strings are left-aligned by default; numbers are right-aligned.

```python
print(f"[{'cat':10}]")
print(f"[{42:10}]")
print(f"[{'cat':>10}]")
print(f"[{'cat':^10}]")
print(f"[{42:<10}]")
print(f"[{'toolong':3}]")
```

Output:

```text
[cat       ]
[        42]
[       cat]
[   cat    ]
[42        ]
[toolong]
```

Like the padding methods, width never cuts. If the value is longer, it is shown in full.

### Fill

A single fill character goes just before the alignment sign. The alignment sign must be present for a fill to be allowed.

```python
print(f"{'menu':*^12}")
print(f"{7:0>3}")
print(f"{'end':.<10}|")
```

Output:

```text
****menu****
007
end.......|
```

### Precision and types for numbers

The **type** letter at the end chooses how a number is written. The **precision** (a dot and a number) means different things for different types.

| Type | Meaning | `1234.5678` with `.2` |
|---|---|---|
| `f` | fixed point, precision = digits after the point | `1234.57` |
| `e` | scientific notation | `1.23e+03` |
| `g` | general: shorter of f or e, precision = significant digits | `1.2e+03` |
| `%` | multiply by 100, show as percent with `f` | `123456.78%` |
| `d` | integer in decimal | (integers only) |
| `b`, `o`, `x`, `X` | integer in binary, octal, hex, HEX | (integers only) |
| `s` | string (the default for strings) | |

```python
x = 1234.5678
print(f"{x:.2f}")
print(f"{x:.0f}")
print(f"{x:.3e}")
print(f"{x:.3g}")
print(f"{0.4567:.1%}")
print(f"{3:.2f}")
print(f"{2.5:.0f} {3.5:.0f}")
```

Output:

```text
1234.57
1235
1.235e+03
1.23e+03
45.7%
3.00
2 4
```

`.2f` always shows exactly two decimals, even for whole numbers like 3. The last line shows that formatting uses the same round-half-to-even rule as `round()` (core.02): 2.5 becomes 2, and 3.5 becomes 4.

For a string, precision means **maximum length**: it cuts the string. This is the one way to truncate with a format spec.

```python
print(f"[{'Christopher':.5}]")
print(f"[{'Christopher':8.5}]")
```

Output:

```text
[Chris]
[Chris   ]
```

### Thousands separators

Put `,` or `_` before the precision to group digits in threes:

```python
big = 1234567.891
print(f"{big:,}")
print(f"{big:,.2f}")
print(f"{9876543210:_}")
print(f"{255:_b}")
```

Output:

```text
1,234,567.891
1,234,567.89
9_876_543_210
1111_1111
```

With `b`, `o`, `x`, the `_` groups in fours, which makes long binary numbers readable. Note that `,` gives the international style 1,234,567; it does not do the Indian lakh style (12,34,567).

### Sign

| Sign | Effect |
|---|---|
| `-` | only negatives get a sign (the default) |
| `+` | every number gets a sign |
| space | positives get a leading space, so columns line up with negatives |

```python
n = 5
print(f"[{n:+}] [{-n:+}]")
print(f"[{n: }] [{-n: }]")
print(f"[{-0.0001:.2f}] [{-0.0001:z.2f}]")
```

Output:

```text
[+5] [-5]
[ 5] [-5]
[-0.00] [0.00]
```

The `z` option (Python 3.11 and later) turns a negative zero, which looks odd in reports, into a plain zero.

### Zero padding and =

A `0` before the width pads numbers with zeros **after** the sign. The `=` alignment does the same with any fill character.

```python
print(f"{42:05}")
print(f"{-42:05}")
print(f"{-42:*=6}")
print(f"{3.14159:08.3f}")
```

Output:

```text
00042
-0042
-***42
0003.142
```

### Integers in other bases

```python
n = 202
print(f"{n:b} {n:o} {n:x} {n:X}")
print(f"{n:#b} {n:#o} {n:#x}")
print(f"{n:08b}")
print(f"{n:#010b}")
print(f"{65:c}")
```

Output:

```text
11001010 312 ca CA
0b11001010 0o312 0xca
11001010
0b11001010
A
```

`#` adds the prefix (`0b`, `0o`, `0x`). Width includes the prefix, so `#010b` gives ten characters in total. The type `c` turns an integer into the character with that code point.

### Nested fields

Any part of the spec can itself be a `{}` field. This lets the width or precision come from a variable:

```python
width = 12
digits = 3
value = 3.14159265
print(f"[{value:{width}.{digits}f}]")
print(f"[{'title':^{width}}]")
fill = "-"
print(f"[{'x':{fill}>{width}}]")
```

Output:

```text
[       3.142]
[   title    ]
[-----------x]
```

### Format specs on other types

Each type decides what its format spec means. Dates are a good example: `datetime` uses `%` codes like `%d` and `%Y` (you will use `datetime` in core.12).

```python
from datetime import date
d = date(2026, 10, 18)
print(f"{d:%d/%m/%Y}")
print(f"{d:%A, %d %B %Y}")
```

Output:

```text
18/10/2026
Sunday, 18 October 2026
```

### Building a table

Put several fields together, with the same widths on every line, and you get aligned columns:

```python
print(f"{'Item':<10}{'Qty':>5}{'Price':>10}")
print("-" * 25)
print(f"{'Pen':<10}{3:>5}{10.5:>10.2f}")
print(f"{'Notebook':<10}{12:>5}{1250:>10,.2f}")
```

Output:

```text
Item        Qty     Price
-------------------------
Pen           3     10.50
Notebook     12  1,250.00
```

### format() and str.format()

The same spec works outside f-strings:

```python
print(format(0.5, ".0%"))
print("{:>6}|{:<6}|".format("ab", "cd"))
print("{0} {1} {0}".format("x", "y"))
print("{name} is {age}".format(name="Asha", age=20))
```

Output:

```text
50%
    ab|cd    |
x y x
Asha is 20
```

`str.format` is useful when the template is stored separately from the values (for example, a message read from a file). There is also an even older style, `"%d items" % 5`, which you will meet in old code; it works but is less capable.

### Under the hood

When Python sees `{value:spec}`, it calls `format(value, "spec")`, which calls the special method `value.__format__("spec")`. Each type implements its own `__format__`. That is why `.2f` works for floats, `%Y` works for dates, and a spec that a type does not understand raises an error:

```python
print(f"{'abc':.2f}")  # error expected
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    print(f"{'abc':.2f}")  # error expected
            ^^^^^^^^^^^
ValueError: Unknown format code 'f' for object of type 'str'
```

### Predict the output

```python
print(f"[{3.14159:7.2f}]")
print(f"[{'ab':-^6}]")
print(f"{1234567:,}")
print(f"{0.125:.1%}")
print(f"{10:#x} {10:04b}")
print(f"[{-3:05}] [{3:+}]")
print(f"[{'Python':.2}]")
```

<details><summary>Answer</summary>

```text
[   3.14]
[--ab--]
1,234,567
12.5%
0xa 1010
[-0003] [+3]
[Py]
```

- `3.14` padded on the left to 7 characters: `[   3.14]`.
- Centred in 6 with `-` as fill: `[--ab--]`.
- `1,234,567`.
- 12.5 percent: `12.5%`.
- `0xa` and `1010`.
- Zero padding goes after the sign: `[-0003]`, and `+` forces a sign: `[+3]`.
- Precision cuts a string: `[Py]`.

</details>

### Common misconceptions

- "Width cuts long values." It never cuts. Only precision cuts, and only for strings.
- "`.2f` rounds the value." It rounds only the **display**; the variable keeps its full value.
- "`{x:05}` works for strings." Zero padding is for numbers. Use `{x:0>5}` for strings.
- "`,` gives Indian grouping." It groups by thousands only.


---

## 18. Unicode, code points, ord and chr

Computers store numbers, not letters. To store text, everyone must agree on a number for each character. **Unicode** is that agreement, for every writing system in the world: Latin, Devanagari, Chinese, Arabic, emoji, maths symbols and many more. Each character gets a number called its **code point**, written like `U+0041` (hexadecimal) for `A`.

A Python `str` is a sequence of code points. `ord()` gives the code point of a one-character string; `chr()` goes the other way.

```python
print(ord("A"), ord("a"), ord("0"), ord(" "))
print(ord("é"), ord("अ"), ord("🙂"))
print(chr(65), chr(8377), chr(128512))
print(f"U+{ord('é'):04X}")
print(chr(ord("a") + 1))
```

Output:

```text
65 97 48 32
233 2309 128578
A ₹ 😀
U+00E9
b
```

The first 128 code points are the same as the old ASCII standard: digits 48 to 57, uppercase 65 to 90, lowercase 97 to 122. That explains the string ordering rules in section 7: comparison is code point comparison.

### Tricks with code points

Because letters are numbered in order, simple arithmetic does useful things:

```python
letter = "d"
print(ord(letter) - ord("a"))
print(chr(ord("a") + 25))
print(chr(ord("G") + 32))
digit = "7"
print(ord(digit) - ord("0"))
```

Output:

```text
3
z
g
7
```

`ord(letter) - ord("a")` is the letter's position in the alphabet (0 for a). Uppercase and lowercase ASCII letters are exactly 32 apart. In real code use `upper()` and `int()`, which also handle non-English text; these tricks are for understanding and for puzzles like ciphers.

### What counts as one character?

A code point is not always what a person sees as one character. Some visible characters are built from several code points:

```python
composed = "é"
decomposed = "é"
print(composed, decomposed)
print(len(composed), len(decomposed))
print(composed == decomposed)
flag = "🇮🇳"
print(len(flag))
family = "👨‍👩‍👧"
print(len(family))
```

Output:

```text
é é
1 2
False
2
5
```

`"é"` is the letter e followed by a "combining acute accent". It looks the same as the single code point `é`, but the strings are not equal and have different lengths. A flag is two "regional indicator" code points. The family emoji is three people joined by invisible "zero width joiner" characters: five code points.

So there are three different "lengths" of a piece of text:

1. **Code points**: what `len()` counts.
2. **Bytes**: how much space it takes when encoded (next section).
3. **Visible characters** (called *grapheme clusters*): what a human counts. The standard library has no simple function for this.

### Normalisation

To compare text that might be composed differently, **normalise** it first with the `unicodedata` module. Form `NFC` combines characters where possible; `NFD` splits them apart.

```python
import unicodedata
a = "café"
b = "café"
print(a == b)
print(unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b))
print(len(unicodedata.normalize("NFD", a)))
print(unicodedata.name("é"))
```

Output:

```text
False
True
5
LATIN SMALL LETTER E WITH ACUTE
```

Text typed on a keyboard is usually NFC, but text copied from files, Mac file names or web pages may not be. When equality "should" be true but is not, normalisation is the first thing to check. For case-insensitive matching across languages, normalise and then `casefold()`.

### Predict the output

```python
print(ord("B") - ord("A"))
print(chr(ord("z") - 2))
print(len("naïve"), len("😀😀"))
print("Z" < "a", "é" > "z")
```

<details><summary>Answer</summary>

```text
1
x
5 2
True True
```

- Adjacent code points: 1.
- Two before z is `x`.
- `naïve` (with a composed ï) has 5 code points, and each emoji is one code point, so 2.
- `Z` is 90 and `a` is 97: True. `é` is 233 and `z` is 122: True.

</details>

### Common misconceptions

- "A character is one byte." That was roughly true for ASCII in the 1970s. Today a character is a code point, and its size in bytes depends on the encoding.
- "`len()` counts what I see." It counts code points. Emoji flags, families and accents built from combining marks all count as more than one.

---

## 19. Encoding and decoding, UTF-8

Files, networks and disks store **bytes**: numbers from 0 to 255. To save text you must turn each code point into bytes. The rule that does this is an **encoding**. The reverse step, bytes to text, is **decoding**.

```
       encode("utf-8")
  str  --------------->  bytes
  "café"                 b'caf\xc3\xa9'
       <---------------
       decode("utf-8")
```

In Python:

```python
text = "café"
data = text.encode("utf-8")
print(data)
print(type(data))
print(len(text), len(data))
back = data.decode("utf-8")
print(back, back == text)
```

Output:

```text
b'caf\xc3\xa9'
<class 'bytes'>
4 5
café True
```

`text` has 4 code points. Encoded in UTF-8 it takes 5 bytes, because `é` needs two. The `b'...'` display shows a `bytes` object: ASCII-range bytes appear as letters, others as `\x` hex escapes.

### UTF-8

**UTF-8** is the encoding the world has settled on. Almost every web page, Linux system and modern file uses it. It is **variable length**:

| Code points | Bytes in UTF-8 | Examples |
|---|---|---|
| U+0000 to U+007F | 1 | ASCII: `A`, `7`, `?` |
| U+0080 to U+07FF | 2 | `é`, `ñ`, Greek, Arabic |
| U+0800 to U+FFFF | 3 | `अ`, `₹`, Chinese, most other scripts |
| U+10000 and up | 4 | emoji, rare scripts |

```python
print(len("A".encode()), len("é".encode()), len("₹".encode()), len("🙂".encode()))
print("₹".encode("utf-8"))
print("🙂".encode("utf-8").hex(" "))
```

Output:

```text
1 2 3 4
b'\xe2\x82\xb9'
f0 9f 99 82
```

`encode()` with no argument uses UTF-8. Three clever properties made UTF-8 win:

- ASCII text is already valid UTF-8, byte for byte. Old English files just work.
- The first byte of a character tells you how many bytes follow, and continuation bytes look different from first bytes, so a program can find character boundaries anywhere in a file.
- No byte of a multi-byte character ever looks like an ASCII character, so searching for `/` or `\n` in raw bytes is safe.

### Other encodings

Older encodings still appear in old files and Windows systems. Each one is a different table, so the same text gives different bytes:

```python
s = "café"
print(s.encode("utf-8"))
print(s.encode("latin-1"))
print(s.encode("utf-16"))
print(s.encode("utf-16-le"))
```

Output:

```text
b'caf\xc3\xa9'
b'caf\xe9'
b'\xff\xfec\x00a\x00f\x00\xe9\x00'
b'c\x00a\x00f\x00\xe9\x00'
```

`latin-1` uses one byte per character but can only store 256 different characters. `utf-16` uses two or four bytes per character and starts with a two-byte marker (the "byte order mark") that tells the reader which byte comes first.

### The golden rule

> Decode bytes into `str` as soon as they enter your program. Work with `str` inside. Encode back to bytes only when they leave. And always know which encoding the bytes use.

When you open text files in core.09, you will pass `encoding="utf-8"` to `open()` for exactly this reason. Without it, Python uses the system default, which differs between computers.

### Under the hood

Inside CPython, a `str` is not stored as UTF-8. It uses one, two or four bytes for every code point (whichever is enough for the widest character in that string), so that indexing stays instant. UTF-8 is for storage and transfer; the internal form is for speed.

---

## 20. Encoding errors and how to fix them

Two different errors happen when things go wrong, and their names tell you the direction.

**UnicodeEncodeError**: text to bytes failed, because the encoding cannot represent some character.

```python
print("café".encode("ascii"))  # error expected
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    print("café".encode("ascii"))  # error expected
          ~~~~~~~~~~~~~^^^^^^^^^
UnicodeEncodeError: 'ascii' codec can't encode character '\xe9' in position 3: ordinal not in range(128)
```

**UnicodeDecodeError**: bytes to text failed, because the bytes are not valid in the encoding you named.

```python
data = "café".encode("latin-1")
print(data)
print(data.decode("utf-8"))  # error expected
```

Output:

```text
b'caf\xe9'
Traceback (most recent call last):
  File "example.py", line 3, in <module>
    print(data.decode("utf-8"))  # error expected
          ~~~~~~~~~~~^^^^^^^^^
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 3: unexpected end of data
```

Read the message carefully: it names the codec (`utf-8`), the bad byte (`0xe9`) and its position (3). In UTF-8, a byte like `0xe9` announces "a three-byte character starts here", but the data ends straight after it, so the decoder gives up. The real cause is simpler: these bytes were written as latin-1 but are being read as UTF-8. The fix is to decode with the encoding that was really used: `data.decode("latin-1")`.

### The errors= argument

Both `encode()` and `decode()` take an `errors` argument that says what to do with characters that do not fit. The default is `"strict"`, which raises the errors above.

```python
s = "café 🙂"
print(s.encode("ascii", errors="ignore"))
print(s.encode("ascii", errors="replace"))
print(s.encode("ascii", errors="xmlcharrefreplace"))
print(s.encode("ascii", errors="backslashreplace"))
bad = b"caf\xe9"
print(bad.decode("utf-8", errors="replace"))
print(bad.decode("utf-8", errors="ignore"))
print(bad.decode("utf-8", errors="backslashreplace"))
```

Output:

```text
b'caf '
b'caf? ?'
b'caf&#233; &#128578;'
b'caf\\xe9 \\U0001f642'
caf�
caf
caf\xe9
```

| Handler | Effect |
|---|---|
| `strict` | raise an error (default) |
| `ignore` | drop the problem character silently |
| `replace` | `?` when encoding; `�` (the replacement character) when decoding |
| `backslashreplace` | write a Python escape like `\xe9` |
| `xmlcharrefreplace` | (encoding only) write an HTML entity like `&#233;` |

`ignore` and `replace` **lose information**. Use them when you prefer imperfect text over a crash, such as when showing a messy log file, and never when the data matters, such as when saving a user's name. The real fix for a decode error is to find out the correct encoding.

### Mojibake

When bytes are decoded with the wrong encoding and no error happens, you get **mojibake** (a Japanese word for "character transformation"): garbled text like `cafÃ©`. It is common because latin-1 can decode *any* bytes without failing.

```python
right = "café"
garbled = right.encode("utf-8").decode("latin-1")
print(garbled)
fixed = garbled.encode("latin-1").decode("utf-8")
print(fixed)
```

Output:

```text
cafÃ©
café
```

The repair reverses the mistake: encode with the wrong encoding to get the original bytes back, then decode with the right one. This works only if no information was lost along the way.

### Predict the output

```python
print(len("₹100".encode("utf-8")))
print("Ünï".encode("ascii", errors="replace"))
print(b"\xe2\x82\xb9".decode("utf-8"))
print("ok".encode("utf-16-le"))
```

<details><summary>Answer</summary>

```text
6
b'?n?'
₹
b'o\x00k\x00'
```

- `₹` takes 3 bytes and `100` takes 3: 6.
- Two non-ASCII letters become `?`: `b'?n?'`.
- Those three bytes are the UTF-8 form of `₹`.
- UTF-16 little-endian uses two bytes per ASCII character, the second being zero: `b'o\x00k\x00'`.

</details>

### Common misconceptions

- "Encoding errors mean the text is corrupt." Usually the text is fine; it was just decoded with the wrong encoding.
- "Use `errors='ignore'` to fix encoding problems." That hides the problem by throwing data away.
- "`encode` is for decoding bytes." `str.encode` goes from text to bytes; `bytes.decode` goes from bytes to text. A `str` has no `decode` method at all.

---

## 21. bytes and bytearray

### bytes

A `bytes` object is an immutable sequence of integers from 0 to 255. Its literal has a `b` in front, and may contain only ASCII characters and escapes.

```python
b = b"Hi!\x00\xff"
print(b)
print(len(b))
print(b[0], b[-1])
print(b[0:2])
print(list(b))
print(bytes([72, 105]))
print(bytes.fromhex("48 69 21"))
print(b"Hi".hex())
```

Output:

```text
b'Hi!\x00\xff'
5
72 255
b'Hi'
[72, 105, 33, 0, 255]
b'Hi'
b'Hi!'
4869
```

The one surprise: **indexing a bytes object gives an int**, not a one-byte bytes object. `b[0]` is `72`. Slicing gives bytes: `b[0:2]` is `b'Hi'`. This is the most common bytes mistake.

`bytes` has most of the string methods (`split`, `replace`, `startswith`, `upper`, `strip`, `find`, and so on), but they take bytes arguments:

```python
data = b"name=asha;city=pune"
print(data.split(b";"))
print(data.upper())
print(data.replace(b"asha", b"ravi"))
```

Output:

```text
[b'name=asha', b'city=pune']
b'NAME=ASHA;CITY=PUNE'
b'name=ravi;city=pune'
```

### str and bytes do not mix

```python
print("abc" == b"abc")
print("abc" + b"def")  # error expected
```

Output:

```text
False
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    print("abc" + b"def")  # error expected
          ~~~~~~^~~~~~~~
TypeError: can only concatenate str (not "bytes") to str
```

`"abc" == b"abc"` is `False`, quietly. Adding them is an error. Python 3 keeps text and bytes strictly apart, so you are forced to choose an encoding whenever you cross over. That strictness prevents a whole class of bugs that troubled Python 2.

### bytearray

A `bytearray` is the **mutable** version of `bytes`. You can change it in place, which makes it useful for building or editing binary data.

```python
buf = bytearray(b"hello")
buf[0] = ord("J")
print(buf)
buf.extend(b" world")
print(buf)
buf[0:5] = b"HELLO"
print(buf.decode())
print(bytes(buf))
```

Output:

```text
bytearray(b'Jello')
bytearray(b'Jello world')
HELLO world
b'HELLO world'
```

Assigning to one position needs an integer (here `ord("J")`), because each position holds an integer. Slice assignment takes bytes.

### When will you use bytes?

Reading images, audio or any non-text file; network sockets; hashing and encryption (core.17 and beyond); and whenever you must control the exact encoding. For ordinary text work, stay with `str`.

### Predict the output

```python
b = b"ABC"
print(b[1])
print(b[1:2])
print(b[::-1])
ba = bytearray(b)
ba[0] = 97
print(ba.decode())
print(len("é".encode()), len(b"\xc3\xa9".decode()))
```

<details><summary>Answer</summary>

```text
66
b'B'
b'CBA'
aBC
2 1
```

- Indexing gives the integer 66.
- Slicing gives bytes: `b'B'`.
- Reversing works like strings: `b'CBA'`.
- 97 is `a`: `aBC`.
- Two bytes encode one code point: 2 and 1.

</details>

---

## 22. The string module

The `string` module holds useful constants and one handy function.

```python
import string
print(string.ascii_lowercase)
print(string.ascii_uppercase)
print(string.digits)
print(string.punctuation)
print(repr(string.whitespace))
print(string.hexdigits)
print(len(string.ascii_letters))
```

Output:

```text
abcdefghijklmnopqrstuvwxyz
ABCDEFGHIJKLMNOPQRSTUVWXYZ
0123456789
!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
' \t\n\r\x0b\x0c'
0123456789abcdefABCDEF
52
```

These save you typing (and typos) when you need "all the punctuation" or "every lowercase letter". For example, `text.strip(string.punctuation)` removes punctuation from both ends of a word.

### capwords

`string.capwords(s)` splits `s` into words with `split()`, capitalises each word, and joins them with single spaces. Unlike `title()`, it does not treat apostrophes as word breaks, and it also collapses extra spaces. It is not perfect either: `o'neil's` becomes `O'neil's`.

```python
import string
s = "they're   o'neil's   friends"
print(s.title())
print(string.capwords(s))
```

Output:

```text
They'Re   O'Neil'S   Friends
They're O'neil's Friends
```

### Template

`string.Template` does simple `$name` substitution. It is safer than f-strings when the template comes from a user, because it cannot run arbitrary expressions.

```python
from string import Template
t = Template("Dear $name, your balance is $amount.")
print(t.substitute(name="Asha", amount="Rs 500"))
print(t.safe_substitute(name="Ravi"))
```

Output:

```text
Dear Asha, your balance is Rs 500.
Dear Ravi, your balance is $amount.
```

`safe_substitute` leaves unknown placeholders alone instead of raising an error.

---

## 23. The textwrap module

`textwrap` reshapes paragraphs for fixed-width output, like a terminal or a plain-text email.

```python
import textwrap
text = ("Python strings are immutable sequences of Unicode code points. "
        "Every method returns a new string.")
print(textwrap.fill(text, width=30))
print()
print(textwrap.wrap(text, width=40))
```

Output:

```text
Python strings are immutable
sequences of Unicode code
points. Every method returns a
new string.

['Python strings are immutable sequences', 'of Unicode code points. Every method', 'returns a new string.']
```

- `textwrap.wrap(text, width)` returns a list of lines, each at most `width` characters, broken at spaces.
- `textwrap.fill(text, width)` does the same and joins the lines with newlines. It is `"\n".join(textwrap.wrap(...))`.

More useful tools:

```python
import textwrap
print(textwrap.shorten("The quick brown fox jumps over the lazy dog", width=20))
print(textwrap.shorten("Short title", width=20))
print(textwrap.shorten("Supercalifragilistic expialidocious", width=15, placeholder="..."))
print(textwrap.indent("line one\nline two", "> "))
print(textwrap.fill("a b c d e f g h", width=7, initial_indent="* ", subsequent_indent="  "))
code = """
    def f():
        return 1
"""
print(textwrap.dedent(code).strip())
```

Output:

```text
The quick [...]
Short title
...
> line one
> line two
* a b c
  d e f
  g h
def f():
    return 1
```

- `shorten` collapses whitespace and, only if the text is too long, cuts it at a word boundary and adds a placeholder (`[...]` by default). If a single word does not fit, you get just the placeholder. Short text comes back unchanged. That "only if needed" behaviour is useful when you cannot write an `if` yet.
- `indent` adds a prefix to every line.
- `dedent` removes common leading whitespace, which is handy for triple-quoted strings inside indented code.
- `initial_indent` and `subsequent_indent` make hanging indents, as used for bullet lists.

### Common misconceptions

- "`wrap` cuts words in half." By default it breaks only at spaces. A single word longer than the width is split, though, unless you pass `break_long_words=False`.
- "`fill` prints the text." It returns a string; you still need `print`.

---

## 24. translate and maketrans

`replace` swaps one substring. When you need to change or delete **many single characters at once**, use `str.translate()` with a table made by `str.maketrans()`.

`str.maketrans` takes up to three arguments:

1. A string of characters to replace.
2. A string of the same length with their replacements (character 1 maps to character 1, and so on).
3. Optionally, a string of characters to delete.

```python
table = str.maketrans("abc", "xyz")
print("aabbcc cab".translate(table))
leet = str.maketrans("aeio", "4310")
print("elite coding".translate(leet))
```

Output:

```text
xxyyzz zxy
3l1t3 c0d1ng
```

### Deleting characters

The third argument lists characters to remove. Combined with `string.punctuation`, it strips all ASCII punctuation in one call:

```python
import string
no_punct = str.maketrans("", "", string.punctuation)
s = "Hello, world! It's 9:30 a.m."
print(s.translate(no_punct))
no_vowels = str.maketrans("", "", "aeiouAEIOU")
print("Programming in Python".translate(no_vowels))
```

Output:

```text
Hello world Its 930 am
Prgrmmng n Pythn
```

### Building tables with slicing

Since the two strings only need to line up, slicing can build clever tables. A Caesar cipher shifts every letter by a fixed amount, wrapping from z back to a:

```python
import string
lower = string.ascii_lowercase
shift = 3
table = str.maketrans(lower, lower[shift:] + lower[:shift])
print(lower[shift:] + lower[:shift])
secret = "attack at dawn".translate(table)
print(secret)
undo = str.maketrans(lower[shift:] + lower[:shift], lower)
print(secret.translate(undo))
```

Output:

```text
defghijklmnopqrstuvwxyzabc
dwwdfn dw gdzq
attack at dawn
```

`lower[3:] + lower[:3]` is the alphabet rotated by three: `defghijklmnopqrstuvwxyzabc`. Position 0 (`a`) lines up with `d`, and so on. Characters not in the table, like spaces, pass through unchanged.

### Dictionary form

`maketrans` can also take a dictionary (core.05) mapping single characters to strings of any length, or to `None` for deletion:

```python
table = str.maketrans({"&": "and", "@": "at", "#": None})
print("rock & roll @ home #fun".translate(table))
```

Output:

```text
rock and roll at home fun
```

### Under the hood

`maketrans` builds a dictionary from **code point numbers** to code points, strings or `None`. You can see it:

```python
print(str.maketrans("ab", "xy", "!"))
```

Output:

```text
{97: 120, 98: 121, 33: None}
```

`translate` walks the string once, looking up each character's code point in the table. One pass, no matter how many characters are in the table. Chaining ten `replace` calls would walk the string ten times.

### Predict the output

```python
t = str.maketrans("lo", "01", " ")
print("hello world".translate(t))
print("abc".translate(str.maketrans("abc", "bca")))
```

<details><summary>Answer</summary>

```text
he001w1r0d
bca
```

- `l` becomes `0`, `o` becomes `1`, spaces are deleted: `he001w1r0d`.
- Every character is looked up once in the original table, so there is no chain reaction: a to b, b to c, c to a gives `bca`.

</details>

### Common misconceptions

- "`translate` replaces words." It works one character at a time. Use `replace` for words.
- "The first two arguments can be different lengths." They must be the same length, or `maketrans` raises `ValueError`.

---

## Summary

- A `str` is an immutable sequence of Unicode code points. A single character is a string of length 1.
- Use either quote type. Escapes like `\n`, `\t`, `\\`, `é` write special characters; raw strings `r"..."` turn escapes off; triple quotes span lines. `repr()` shows hidden characters.
- Indexing `s[i]` starts at 0; negative indices count from the end; out of range is an `IndexError`.
- Slicing `s[start:stop:step]` includes start, excludes stop, clips out-of-range bounds silently, and walks backwards with a negative step. `s[::-1]` reverses.
- `+` joins, `*` repeats, `in` tests for a substring. Comparison is by code point, so uppercase sorts before lowercase and `"10" < "9"`.
- Methods never change a string; they return new ones. Store the result. Build text with `join`, not repeated `+=`.
- Case: `upper`, `lower`, `title`, `capitalize`, `swapcase`, and `casefold` for comparing.
- Searching: `in`, `find`/`rfind` (return -1, a valid index, when missing), `index`/`rindex` (raise `ValueError`), `count` (non-overlapping), `startswith`/`endswith` (accept a tuple).
- Cleaning: `strip` family takes a set of characters; `removeprefix`/`removesuffix` remove one exact piece; `replace` swaps every occurrence.
- `split()` with no argument splits on whitespace runs; `split(sep)` keeps empty fields. `rsplit` and `maxsplit` limit cuts; `splitlines` handles line endings; `partition`/`rpartition` always return three parts.
- `is` methods test every character and are `False` for `""`; `isdigit` is not "is a number".
- `center`, `ljust`, `rjust`, `zfill` pad and never cut.
- f-strings evaluate expressions; `!r` shows repr; `{x=}` debugs. The format spec is `[[fill]align][sign][z][#][0][width][grouping][.precision][type]`, and its parts can be nested fields.
- `ord` and `chr` convert between characters and code points. `len` counts code points, not bytes and not visible characters. Normalise with `unicodedata.normalize("NFC", s)` before comparing.
- `encode` turns `str` into `bytes`; `decode` turns `bytes` into `str`. UTF-8 uses 1 to 4 bytes per code point. `errors=` chooses strict, ignore, replace, backslashreplace or xmlcharrefreplace.
- `bytes` is immutable and indexes to integers; `bytearray` is mutable. Text and bytes never mix silently.
- `string` gives constants and `capwords`; `textwrap` gives `wrap`, `fill`, `shorten`, `indent`, `dedent`; `translate` with `maketrans` maps or deletes many characters in one pass.

## Learning outcomes

After this chapter you should be able to:

- [ ] Write any string literal, including quotes, backslashes, Unicode escapes, raw strings and multiline strings, and predict its length.
- [ ] Predict the result of any index or slice, including negative indices, steps, and out-of-range bounds.
- [ ] Choose the right method for a text task (searching, cleaning, splitting, joining, testing, padding) without writing a loop.
- [ ] Explain why `find` returning -1 is dangerous and when to use `in`, `find`, `index` or `partition` instead.
- [ ] Format numbers, tables and dates with f-strings using width, alignment, fill, sign, grouping, precision and type.
- [ ] Explain why strings are immutable and why `join` is preferred over `+=` for building text.
- [ ] Explain code points, `ord`, `chr`, and why `len` may differ from what you see.
- [ ] Explain the difference between `str` and `bytes`, encode and decode with UTF-8, and fix a `UnicodeDecodeError` or mojibake.
- [ ] Use `bytes` and `bytearray` and know that indexing bytes gives integers.
- [ ] Use `string` constants, `textwrap` and `translate`/`maketrans` for bulk text changes.

## Module project

The project for this module is a **text statistics tool**. It reads text and prints a neat, aligned report: character counts (with and without spaces), word counts, line counts, average word length, how often chosen words appear, and the share of the text they make up. You will clean the text with `casefold()`, `translate()` and `split()`, count with `len()` and `count()`, and lay out the report with format specs: fixed-width labels, right-aligned numbers, thousands separators and percentages. Think about the hard cases: empty text, text that is only punctuation, accented words like `café`, and emoji. Problem p048 is a first version of this tool. After core.05 and core.07 you can extend it to count *every* word's frequency with a dictionary and to read whole files.

## Further reading

All links are to the official Python documentation.

- Text sequence type (str): https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
- String methods: https://docs.python.org/3/library/stdtypes.html#string-methods
- String literals and escape sequences: https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals
- f-strings: https://docs.python.org/3/reference/lexical_analysis.html#f-strings
- Format specification mini-language: https://docs.python.org/3/library/string.html#format-specification-mini-language
- Common sequence operations (indexing, slicing): https://docs.python.org/3/library/stdtypes.html#common-sequence-operations
- Unicode HOWTO: https://docs.python.org/3/howto/unicode.html
- Standard encodings: https://docs.python.org/3/library/codecs.html#standard-encodings
- Error handlers: https://docs.python.org/3/library/codecs.html#error-handlers
- bytes and bytearray: https://docs.python.org/3/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview
- string module: https://docs.python.org/3/library/string.html
- textwrap module: https://docs.python.org/3/library/textwrap.html
- unicodedata module: https://docs.python.org/3/library/unicodedata.html
- str.maketrans: https://docs.python.org/3/library/stdtypes.html#str.maketrans

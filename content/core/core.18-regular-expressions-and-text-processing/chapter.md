# Chapter 18: Regular expressions and text processing

Most of the data a programmer meets is not a neat list of numbers. It is **text**: log files, form inputs, CSV exports with odd spacing, e-mails, configuration files, chat messages, error reports. Chapter 3 gave you the string methods: `split`, `strip`, `find`, `startswith`, `replace`. They are simple and fast, and they solve many problems. But sooner or later you meet a question like these:

- "Find every date in this report, whether it is written `05/03/2024` or `2024-03-05`."
- "Is this a valid Indian mobile number, with or without `+91`, with or without a space in the middle?"
- "From each line of this log, pull out the time, the level, the module name and the message."
- "Replace every `{{ name }}` in this template with the right value."

You can solve each of them with loops and `find` and many `if`s. The code will be long, fragile, and hard to read a week later. A **regular expression** (a *regex*, or a *pattern*) describes the **shape** of the text you want in one short line, and Python's `re` module does the searching for you.

This chapter has two learning outcomes, and every section serves one of them:

1. **Extract structured fields from messy text with named groups.** By the end you will turn a line like `2024-03-05 10:42:17 ERROR [payments] card declined` into a Python object with a timestamp, a level, a module and a message.
2. **Explain why a pattern is slow and rewrite it.** Some innocent-looking patterns take seconds, or years, on certain inputs. You will learn why, how to spot them, and how to fix them, and also when regex is simply the wrong tool.

Regular expressions have a reputation for being cryptic. They are, if you meet them all at once. Here you will build them up one small piece at a time, and every piece is tried on real strings. Read each example, **predict** the output, then compare.

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14** on Linux. Timings change from machine to machine and run to run; they are labelled *machine-specific*. The course supports Python 3.11 and newer; when a feature is newer than that, the text says so.

## Table of contents

1. [Why regex (and when string methods are enough)](#1-why-regex-and-when-string-methods-are-enough)
2. [First patterns: `search`, `match`, `fullmatch` and Match objects](#2-first-patterns-search-match-fullmatch-and-match-objects)
3. [Raw strings and escaping](#3-raw-strings-and-escaping)
4. [Character classes](#4-character-classes)
5. [Quantifiers and anchors](#5-quantifiers-and-anchors)
6. [`findall`, `finditer`, `split`, and validation with `fullmatch`](#6-findall-finditer-split-and-validation-with-fullmatch)
7. [Groups and alternation](#7-groups-and-alternation)
8. [Named groups and backreferences](#8-named-groups-and-backreferences)
9. [Greedy versus lazy](#9-greedy-versus-lazy)
10. [Lookahead and lookbehind](#10-lookahead-and-lookbehind)
11. [Flags and verbose patterns](#11-flags-and-verbose-patterns)
12. [`re.sub`, `re.subn` and compiled patterns](#12-resub-resubn-and-compiled-patterns)
13. [Catastrophic backtracking, and when not to use regex](#13-catastrophic-backtracking-and-when-not-to-use-regex)
14. [Project: a log analyser](#14-project-a-log-analyser)
15. [Common traps and summary](#15-common-traps-and-summary)

## 1. Why regex (and when string methods are enough)

### 1.1 A problem string methods find hard

Suppose a user types a phone number into a form, and you want to know if the text **contains** a six-digit Indian PIN code (a postal code), such as `560001`. With string methods, you must walk through the text yourself:

```python
def has_pin_by_hand(text):
    for i in range(len(text) - 5):
        chunk = text[i:i + 6]
        if chunk.isdigit():
            before_ok = i == 0 or not text[i - 1].isdigit()
            after_ok = i + 6 == len(text) or not text[i + 6].isdigit()
            if before_ok and after_ok:
                return True
    return False

for t in ["Bengaluru 560001", "call 98450 12345", "id 1234567", "PIN:110011."]:
    print(f"{t!r:22} {has_pin_by_hand(t)}")
```
```text
'Bengaluru 560001'     True
'call 98450 12345'     False
'id 1234567'           False
'PIN:110011.'          True
```

It works, but look at the effort: index arithmetic, two boundary checks, and an off-by-one waiting to happen in `range(len(text) - 5)`. Now the same question with a regular expression:

```python
import re

for t in ["Bengaluru 560001", "call 98450 12345", "id 1234567", "PIN:110011."]:
    print(f"{t!r:22} {re.search(r'(?<!\d)\d{6}(?!\d)', t) is not None}")
```
```text
'Bengaluru 560001'     True
'call 98450 12345'     False
'id 1234567'           False
'PIN:110011.'          True
```

You cannot read that pattern yet, and that is fine. By section 10 every symbol in it will be familiar: `\d{6}` means "six digits", and the two odd-looking parts around it mean "not right after a digit" and "not right before a digit". The point for now: **the pattern describes what the text looks like, and the `re` module does the walking**.

### 1.2 What a regular expression is

A regular expression is a small **language for describing sets of strings**. The pattern `cat` describes exactly one string. The pattern `c[aou]t` describes three: `cat`, `cot`, `cut`. The pattern `\d+` describes infinitely many: every non-empty run of digits.

The `re` module takes a pattern and some text, and answers questions such as:

| Question | Function |
|---|---|
| Is there a match anywhere? Where is the first one? | `re.search` |
| Does the text **start** with a match? | `re.match` |
| Is the **whole** text a match? | `re.fullmatch` |
| Give me every match | `re.findall`, `re.finditer` |
| Cut the text wherever the pattern matches | `re.split` |
| Replace every match | `re.sub`, `re.subn` |

Behind the scenes, `re` **compiles** the pattern into a small program, then runs that program over the text, trying the pattern at position 0, then 1, then 2, and so on, until it finds a match or runs out of text. Keep this picture in mind; it explains most of the behaviour in this chapter, including the slow cases in section 13.

### 1.3 When string methods are enough

Regex is powerful, and that is exactly why people overuse it. **If a string method does the job, use the string method.** It is faster, it cannot hide a bug in a symbol you misread, and every reader understands it.

| Task | Use this, not regex |
|---|---|
| Does the text contain `"error"`? | `"error" in text` |
| Does it start / end with something? | `text.startswith("http")`, `name.endswith((".jpg", ".png"))` |
| Split on one fixed separator | `line.split(",")` |
| Split on runs of whitespace | `line.split()` (no argument) |
| Replace a fixed word | `text.replace("colour", "color")` |
| Is it all digits? | `s.isdigit()` (careful: see section 4.5) |
| Remove spaces at the ends | `s.strip()` |
| Change case | `s.lower()`, `s.casefold()` |

Use regex when the thing you look for has a **shape** rather than a fixed spelling: "some digits, a slash, some digits", "a word repeated twice", "anything between square brackets", "a date in one of three formats".

### 1.4 A rule of thumb

Ask two questions:

1. **Can I describe what I want in one sentence that mentions "any", "some", "one of", or "optional"?** ("any digit", "some letters", "one of `-` or `/`", "an optional `+91`".) Then regex fits.
2. **Does the text have nesting, like brackets inside brackets, tags inside tags, or objects inside objects?** Then regex is the wrong tool; use a real parser (section 13.5).

#### Try it 1.1

For each task, decide: string method or regex? Then check the answer.

1. Check whether a file name ends in `.csv`.
2. Find all words that start with a capital letter.
3. Split `"a,b,c"` into three parts.
4. Split `"a, b;c ; d"` on commas or semicolons, with any spaces around them.
5. Check whether a string looks like an e-mail address.

<details><summary>Answer</summary>

1. String method: `name.endswith(".csv")`.
2. Regex: "a capital letter, then some letters" is a shape.
3. String method: `"a,b,c".split(",")`.
4. Regex: there are two possible separators and a variable amount of space. `re.split(r"\s*[,;]\s*", s)` (section 6).
5. Regex, for a rough check ("something, an `@`, something, a dot, something"). A *perfect* e-mail check is famously hard even with regex; real systems send a confirmation mail instead.

</details>

## 2. First patterns: `search`, `match`, `fullmatch` and Match objects

### 2.1 `re.search`: find the first match anywhere

The most useful function is `re.search(pattern, text)`. It scans the text from left to right and stops at the **first** place where the pattern matches. It returns a **Match object** if it finds one, and `None` if it does not.

```python
import re

m = re.search(r"cat", "the cat sat on the cat mat")
print(m)
print(re.search(r"dog", "the cat sat"))
```
```text
<re.Match object; span=(4, 7), match='cat'>
None
```

The Match object's printed form already tells you a lot: `span=(4, 7)` means the match covers `text[4:7]`, and `match='cat'` is the matched text. Only the **first** `cat` was found; `search` stops there.

Because `search` returns `None` when nothing matches, the usual shape of code is:

```python
import re

for text in ["order 42 shipped", "no number here"]:
    m = re.search(r"\d+", text)
    if m:
        print("found", m.group(), "in", repr(text))
    else:
        print("nothing in", repr(text))
```
```text
found 42 in 'order 42 shipped'
nothing in 'no number here'
```

A Match object is always "truthy", and `None` is "falsy", so `if m:` reads naturally. (`\d+` means "one or more digits"; sections 4 and 5 explain the symbols.)

### 2.2 The Match object

A Match object remembers **what** matched and **where**:

| Method | Gives |
|---|---|
| `m.group()` or `m.group(0)` | the whole matched text |
| `m.start()` | index where the match begins |
| `m.end()` | index just **after** the match ends |
| `m.span()` | `(m.start(), m.end())` |
| `m.string` | the text that was searched |
| `m.re` | the compiled pattern that was used |

```python
import re

text = "Invoice INV-2024-0042 is due"
m = re.search(r"INV-\d+-\d+", text)
print(m.group())
print(m.start(), m.end(), m.span())
print(text[m.start():m.end()])
print(m.re.pattern)
```
```text
INV-2024-0042
8 21 (8, 21)
INV-2024-0042
INV-\d+-\d+
```

`start` and `end` follow the same rule as slicing: the end index is **not** included, so `text[m.start():m.end()]` is always the matched text. That rule also means `m.end() - m.start()` is the length of the match.

**The classic crash.** If there is no match, `re.search` returns `None`, and `None` has no `.group()`:

```python
import re

m = re.search(r"\d+", "no digits")
try:
    print(m.group())
except AttributeError as e:
    print("AttributeError:", e)
```
```text
AttributeError: 'NoneType' object has no attribute 'group'
```

When you see `'NoneType' object has no attribute 'group'`, the pattern did not match. Always check `if m:` (or be sure, by the problem's rules, that a match must exist).

### 2.3 `re.match` and `re.fullmatch`

Two cousins of `search` try the pattern at fixed places:

- `re.match(p, text)` only tries at **position 0**. The match must start at the beginning, but it may end anywhere.
- `re.fullmatch(p, text)` only succeeds if the pattern matches the **entire** text, from the first character to the last.

```python
import re

for text in ["42 apples", "apples 42", "42"]:
    print(f"{text!r:12}",
          "search:", re.search(r"\d+", text) is not None,
          "match:", re.match(r"\d+", text) is not None,
          "fullmatch:", re.fullmatch(r"\d+", text) is not None)
```
```text
'42 apples'  search: True match: True fullmatch: False
'apples 42'  search: True match: False fullmatch: False
'42'         search: True match: True fullmatch: True
```

Read the table row by row:

- `"42 apples"`: digits at the start, so `search` and `match` succeed; but the whole string is not digits, so `fullmatch` fails.
- `"apples 42"`: digits exist (search), but not at the start (match fails).
- `"42"`: all three succeed.

Which one to use?

- **Finding** something inside text: `search`.
- **Validating** that an input has exactly a form (a PIN, a roll number, a date): `fullmatch`. This is the safe choice for validation; section 6.4 shows the bugs that `match` and `search` cause there.
- `match` is rarely what you want. It exists mostly for historical reasons, and it misleads people who expect it to check the whole string.

#### Try it 2.1

Predict each line (`True` or `False`), then run it.

```python
import re
print(re.match(r"py", "python") is not None)
print(re.match(r"thon", "python") is not None)
print(re.search(r"thon", "python") is not None)
print(re.fullmatch(r"py", "python") is not None)
print(re.fullmatch(r"python", "python") is not None)
print(re.search(r"Py", "python") is not None)
```

<details><summary>Answer</summary>

```text
True
False
True
False
True
False
```

`match` only looks at the start, so `thon` fails there although `search` finds it. `fullmatch` needs the whole string. The last one is `False` because matching is **case-sensitive** by default (section 11 shows `re.IGNORECASE`).

</details>

### 2.4 Literal characters and the special ones

Most characters in a pattern simply match themselves: the pattern `cat` matches the letters `c`, `a`, `t` in that order. A small set of characters are **metacharacters** with special jobs:

```text
.  ^  $  *  +  ?  {  }  [  ]  \  |  (  )
```

You will learn every one of them in this chapter. Until then, remember: **if you want one of these characters literally, put a backslash before it.** `\.` matches a real dot, `\(` a real bracket, `\$` a real dollar sign.

```python
import re

print(re.search(r"3.14", "pi is 3714"))      # . means "any character"
print(re.search(r"3\.14", "pi is 3714"))     # \. means a real dot
print(re.search(r"3\.14", "pi is 3.14"))
```
```text
<re.Match object; span=(6, 10), match='3714'>
None
<re.Match object; span=(6, 10), match='3.14'>
```

The first line is a real bug in disguise: the unescaped dot matched the `7`. A pattern for a price, an IP address or a file extension almost always needs `\.`.

### 2.5 Where the search starts, step by step

It helps to see exactly how `search` works. For the pattern `ab` and the text `"aab"`:

1. Try at position 0: `a` matches `a`; next pattern char `b` versus text `a`: fail.
2. Try at position 1: `a` matches `a`; `b` matches `b`: success. The match is `text[1:3]`.

So the engine **moves the starting point one step at a time** and, at each start, tries to match the whole pattern. The first start that works wins, even if a "better" match exists later. This is called **leftmost** matching, and it is why `re.search(r"\d+", "a1 b2345")` gives `1`, not the longer `2345`.

```python
import re
print(re.search(r"\d+", "a1 b2345").group())
```
```text
1
```

## 3. Raw strings and escaping

### 3.1 Two languages, one backslash

The backslash `\` has a special meaning **twice**:

1. In a normal Python string literal, `\n` is a newline, `\t` a tab, `\\` one backslash (Chapter 3).
2. In a regex pattern, `\d` means "a digit", `\.` means "a real dot", `\b` means "a word boundary", and `\\` means "one real backslash".

When you write a pattern as a normal string, Python processes the backslashes **first**, and only what is left reaches `re`. Sometimes that is harmless, sometimes it silently changes your pattern.

```python
s1 = "\n"
s2 = r"\n"
print(len(s1), repr(s1))
print(len(s2), repr(s2))
print(len("\b"), repr("\b"))
print(len(r"\b"), repr(r"\b"))
```
```text
1 '\n'
2 '\\n'
1 '\x08'
2 '\\b'
```

The prefix `r` makes a **raw string**: Python leaves every backslash exactly as typed. `r"\n"` is two characters, a backslash and an `n`, and the `re` module then decides what they mean.

### 3.2 The `\b` trap

`\b` is the clearest example of why raw strings matter. In Python, `"\b"` is the **backspace character** (code 8). In regex, `\b` means "a word boundary". Without `r`, your pattern contains a backspace, which never appears in normal text:

```python
import re

text = "a cat and a catalogue"
print(re.findall("\bcat\b", text))      # backspace characters: finds nothing
print(re.findall(r"\bcat\b", text))     # word boundaries: finds the word "cat"
```
```text
[]
['cat']
```

No error, no warning, just an empty result. This is the worst kind of bug.

What about `"\d"`? Python does not know the escape `\d`, so it keeps the backslash, and the pattern happens to work. But since Python 3.12, an unknown escape like `"\d"` in a normal string produces a `SyntaxWarning: invalid escape sequence '\d'`, and a future version will make it an error. Do not rely on it.

**The rule: always write regex patterns as raw strings, `r"..."`, even when they contain no backslash.** It costs one letter and removes a whole class of bugs.

### 3.3 Matching a real backslash

To match one backslash in the text, the regex needs `\\` (an escaped backslash). With a raw string, you type exactly that:

```python
import re

path = r"C:\Users\you\notes.txt"
print(path)
print(re.findall(r"\\", path))
print(re.split(r"\\", path))
```
```text
C:\Users\you\notes.txt
['\\', '\\', '\\']
['C:', 'Users', 'you', 'notes.txt']
```

Without a raw string, you would need `"\\\\"`: four backslashes in the source, which become two in the string, which the regex reads as one real backslash. Raw strings make this sane. (Note how `findall` shows each match as `'\\'`: that is the `repr` of a one-character string containing a backslash.)

One small limit: a raw string cannot end in a single backslash (`r"abc\"` is a syntax error), because the backslash still stops the closing quote from ending the string. Patterns rarely need that.

### 3.4 `re.escape`: user text inside a pattern

Often a part of the pattern comes from **data**: a word the user searches for, a product code, a file name. If that data contains metacharacters, they suddenly mean something:

```python
import re

price = "$4.99"
text = "Total: $4.99 or $4199"
print(re.findall(price, text))              # $ is an anchor and . is "any char"
print(re.escape(price))
print(re.findall(re.escape(price), text))
```
```text
[]
\$4\.99
['$4.99']
```

`re.escape(s)` puts a backslash before every character that has a special meaning, so the result matches `s` **literally**. Use it every time you build a pattern from text you did not write yourself:

```python
import re

def count_word(text, word):
    pattern = r"\b" + re.escape(word) + r"\b"
    return len(re.findall(pattern, text))

print(count_word("C++ and C are languages; c++ fans love C++.", "C++"))
```
```text
0
```

Wait: three `C++` appear (one lowercase), and the answer is 0. Without `re.escape`, `C++` would even be an error ("multiple repeat"). With it, the pattern is valid, but `\b` after `+` needs a **word** character on one side, and `+` and the following space are both non-word characters. Word boundaries only make sense next to letters, digits or `_`. You will meet `\b` properly in section 5.4; the lesson here is that `re.escape` fixes the meaning of the user's text, and you must still think about what surrounds it.

#### Try it 3.1

Predict each line.

```python
import re
print(len("a\tb"), len(r"a\tb"))
print(re.escape("1+1=2"))
print(re.escape("hello_world 2"))
print(re.search(re.escape("a.c"), "abc"))
print(re.search("a.c", "abc").group())
```

<details><summary>Answer</summary>

```text
3 4
1\+1=2
hello_world\ 2
None
abc
```

`"\t"` is one tab character, `r"\t"` is two characters. `re.escape` escapes `+` and `=`, and also the space (spaces matter in verbose patterns, section 11), but leaves letters, digits and `_` alone. An escaped `a\.c` needs a real dot, so it does not match `abc`; the unescaped `a.c` does.

</details>

## 4. Character classes

### 4.1 `[...]`: one character from a set

Square brackets describe **one** character chosen from a set. `[aeiou]` matches one vowel. `c[aou]t` matches `cat`, `cot` or `cut`, but not `cet` and not `caat`.

```python
import re

print(re.findall(r"c[aou]t", "cat cot cut cet caat"))
print(re.findall(r"[aeiou]", "regular expression"))
print(re.findall(r"gr[ae]y", "grey or gray, not groy"))
```
```text
['cat', 'cot', 'cut']
['e', 'u', 'a', 'e', 'e', 'i', 'o']
['grey', 'gray']
```

Remember: **a class always matches exactly one character** (unless a quantifier follows it, section 5). `[aeiou]` does not match `"ae"`.

### 4.2 Ranges

Inside a class, a hyphen between two characters means a **range**: `[a-z]` is any lowercase ASCII letter, `[0-9]` any ASCII digit, `[A-Fa-f0-9]` a hex digit. You can combine several ranges and single characters in one class:

```python
import re

print(re.findall(r"[A-Z]", "New Delhi, India"))
print(re.findall(r"[0-9a-fA-F]", "Colour #1fA9zz"))
print(re.fullmatch(r"[A-Z][a-z][a-z]", "Jan") is not None)
print(re.fullmatch(r"[A-Z][a-z][a-z]", "jan") is not None)
```
```text
['N', 'D', 'I']
['C', '1', 'f', 'A', '9']
True
False
```

Ranges follow **character codes** (Unicode code points). `[A-z]` looks like "all letters" but also includes the six characters between `Z` and `a` in the code table: `[ \ ] ^ _` and the backtick. Write `[A-Za-z]`.

To put a literal hyphen in a class, write it **first or last** (`[-+]`, `[a-z-]`) or escape it (`[a\-z]`):

```python
import re

print(re.findall(r"[a-c]", "a-b-c"))       # a range: a, b, c
print(re.findall(r"[ac-]", "a-b-c"))       # a, c and a real hyphen
print(re.findall(r"[-+]?[0-9]", "+5 -3 7"))
```
```text
['a', 'b', 'c']
['a', '-', '-', 'c']
['+5', '-3', '7']
```

(`?` means "optional"; section 5.)

### 4.3 Negation with `^`

If the first character inside the brackets is `^`, the class is **negated**: it matches any **one** character that is **not** in the set.

```python
import re

print(re.findall(r"[^aeiou ]", "hello world"))
print(re.findall(r"[^0-9]", "a1b2!"))
print(re.sub(r"[^A-Za-z0-9]", "", "Hello, World! 2024 :)"))
```
```text
['h', 'l', 'l', 'w', 'r', 'l', 'd']
['a', 'b', '!']
HelloWorld2024
```

Three details:

- `^` only negates when it is the **first** character inside `[ ]`. `[a^b]` matches `a`, `^` or `b`. (Outside a class, `^` is an anchor, section 5.)
- A negated class **still consumes one character**. `[^x]` does not mean "nothing here"; it means "one character which is not `x`". So `q[^u]` does not match the `q` at the very end of `"Iraq"`: there is no character after it to match `[^u]`.
- A negated class **does** match a newline, unlike `.`.

Most metacharacters lose their special meaning inside a class: `[.]` is a real dot, `[*+?]` matches one of those three symbols, `[$]` a dollar. Only `\`, `]`, `^` (at the start) and `-` (in the middle) are special inside brackets.

### 4.4 Shorthand classes: `\d \w \s` and their opposites

Some classes are so common that they have short names:

| Shorthand | Meaning (for ASCII text) | Opposite |
|---|---|---|
| `\d` | a digit, like `[0-9]` | `\D`: not a digit |
| `\w` | a "word" character: letter, digit or underscore, like `[A-Za-z0-9_]` | `\W`: not a word character |
| `\s` | whitespace: space, tab, newline, carriage return, form feed, vertical tab | `\S`: not whitespace |

The capital letter is always the opposite. They can appear inside a class too: `[\d.]` is a digit or a dot, `[\w-]` a word character or a hyphen.

```python
import re

text = "Order #A-17 shipped\ton 05/03, qty: 3_000"
print(re.findall(r"\d", text))
print(re.findall(r"\w+", text))
print(re.findall(r"\s", text))
print(re.findall(r"\S+", text))
print(re.findall(r"[\w-]+", text))
```
```text
['1', '7', '0', '5', '0', '3', '3', '0', '0', '0']
['Order', 'A', '17', 'shipped', 'on', '05', '03', 'qty', '3_000']
[' ', ' ', '\t', ' ', ' ', ' ']
['Order', '#A-17', 'shipped', 'on', '05/03,', 'qty:', '3_000']
['Order', 'A-17', 'shipped', 'on', '05', '03', 'qty', '3_000']
```

Look at the second line: `\w+` treats `3_000` as one word (underscore is a word character) but splits `A-17` (hyphen is not). `\S+` gives "everything between spaces", which is the same as `text.split()`; in a real program, use `split()` for that.

### 4.5 Unicode notes: `\d` is bigger than `[0-9]`

The table above said "for ASCII text". Python's `re` works on `str`, which is Unicode, so by default `\d` matches **any Unicode decimal digit**, and `\w` matches letters of **any script**:

```python
import re

print(re.findall(r"\d+", "Price ४५ rupees, or 45"))
print(re.findall(r"[0-9]+", "Price ४५ rupees, or 45"))
print(re.findall(r"\w+", "naïve café नमस्ते"))
print(re.findall(r"\d+", "Price ४५ rupees, or 45", flags=re.ASCII))
print(int("४५"))
```
```text
['४५', '45']
['45']
['naïve', 'café', 'नमस', 'त']
['45']
45
```

`४५` is "45" in Devanagari digits. `\d` accepts it; `[0-9]` does not. (`int()` accepts it too, so converting is safe.) The `\w+` result for the Hindi word is split in a surprising way: some combining vowel signs are not "word" characters to `re`. Unicode text is genuinely complicated.

What to do:

- When the input must be **ASCII digits** (an account number, a PIN code, an amount for a bank file), write `[0-9]` or pass `re.ASCII` (section 11). Do not let `\d` accept digits your next step cannot handle.
- When you process **human language**, `\w` with Unicode is usually what you want for European accents. For complex scripts, test with real data before you trust it.
- `str.isdigit()` is even wider than `\d` (it accepts superscripts like `²`). For "only 0 to 9", `re.fullmatch(r"[0-9]+", s)` is the precise check.

### 4.6 The dot: any character except newline

The dot `.` matches **any single character except a newline** (`\n`). It is the most-used and most-misused symbol in regex.

```python
import re

print(re.findall(r"b.t", "bat bet b t b\nt bt"))
print(re.findall(r"..", "abcde"))
print(re.search(r"x.y", "x\ny"))
print(re.search(r"x.y", "x\ny", flags=re.DOTALL))
```
```text
['bat', 'bet', 'b t']
['ab', 'cd']
None
<re.Match object; span=(0, 3), match='x\ny'>
```

`b.t` found `bat`, `bet` and `b t` (a space is a character), but not `b\nt` and not `bt` (the dot needs exactly one character). The `re.DOTALL` flag makes the dot match newlines too (section 11).

The dot's weakness is that it matches **too much**. If you know what can appear, say it: `\d` for digits, `[^"]` for "anything but a quote", `[^\]]` for "anything but a closing bracket". Precise classes make patterns both more correct and faster.

#### Try it 4.1

Predict each list.

```python
import re
text = "R2-D2 met C-3PO at 10:45 in bay_7"
print(re.findall(r"[A-Z]", text))
print(re.findall(r"[^A-Za-z ]", text))
print(re.findall(r"\d\d", text))
print(re.findall(r"\w-\w", text))
print(re.findall(r"[.:]", text))
```

<details><summary>Answer</summary>

```text
['R', 'D', 'C', 'P', 'O']
['2', '-', '2', '-', '3', '1', '0', ':', '4', '5', '_', '7']
['10', '45']
['2-D', 'C-3']
[':']
```

Line 3 finds non-overlapping pairs of digits: `10` and `45`. The single digits `2`, `3`, `7` have no digit next to them. In line 4, `\w-\w` matches `2-D` and `C-3`; the second `2` in `R2-D2` is not used because the match `2-D` already consumed the `D`. Line 5: there is no dot in the text, only the colon.

</details>

#### Try it 4.2

Write a pattern that matches a whole string that is a **valid hex colour**: a `#` followed by exactly six hex digits (upper or lower case). Test it on `"#1fA9c0"` (valid), `"#1fA9c"` (too short), `"1fA9c0"` (no `#`) and `"#1fA9g0"` (`g` is not hex).

<details><summary>Answer</summary>

```python
import re
pattern = r"#[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]"
for s in ["#1fA9c0", "#1fA9c", "1fA9c0", "#1fA9g0"]:
    print(s, re.fullmatch(pattern, s) is not None)
```

```text
#1fA9c0 True
#1fA9c False
1fA9c0 False
#1fA9g0 False
```

Repeating the class six times works but is ugly. Section 5 shows the short form: `#[0-9a-fA-F]{6}`. And notice `fullmatch`: with `search`, `"#1fA9c0zz"` would also pass.

</details>

## 5. Quantifiers and anchors

### 5.1 Quantifiers: how many times

A **quantifier** comes right after a piece of pattern and says how many times that piece may repeat:

| Quantifier | Meaning |
|---|---|
| `*` | 0 or more times |
| `+` | 1 or more times |
| `?` | 0 or 1 time (optional) |
| `{n}` | exactly n times |
| `{m,n}` | between m and n times (both included) |
| `{m,}` | m or more times |
| `{,n}` | 0 to n times |

The quantifier applies to the **one item just before it**: a single character, a class, an escape like `\d`, or a group in brackets (section 7). So `ab+` means "`a`, then one or more `b`", **not** "one or more `ab`".

```python
import re

text = "a ab abb abbb b"
print(re.findall(r"ab*", text))
print(re.findall(r"ab+", text))
print(re.findall(r"ab?", text))
print(re.findall(r"ab{2}", text))
print(re.findall(r"ab{1,2}", text))
```
```text
['a', 'ab', 'abb', 'abbb']
['ab', 'abb', 'abbb']
['a', 'ab', 'ab', 'ab']
['abb', 'abb']
['ab', 'abb', 'abb']
```

Look carefully at `ab{1,2}` on `abbb`: it matched `abb` and left the last `b`, because it may take at most two. And `ab?` on `abbb` took `ab` and stopped.

Now the hex colour from Try it 4.2 becomes short, and an Indian PIN code, a year or a time are easy to describe:

```python
import re

print(re.fullmatch(r"#[0-9a-fA-F]{6}", "#1fA9c0") is not None)
print(re.findall(r"\b[0-9]{6}\b", "PIN 560001, phone 9845012345"))
print(re.findall(r"[0-9]{1,2}:[0-9]{2}", "Meet at 9:30 or 10:45, not 1030"))
```
```text
True
['560001']
['9:30', '10:45']
```

### 5.2 Quantifiers are greedy

By default, every quantifier is **greedy**: it takes **as many** repetitions as it can, and gives some back only if the rest of the pattern cannot match otherwise. That is why `\d+` on `"12345"` gives all five digits, not just `1`.

```python
import re

print(re.search(r"\d+", "abc 12345 xyz").group())
print(re.search(r"\d{2,4}", "abc 12345 xyz").group())
print(re.search(r"a.*b", "a1b a2b a3b").group())
```
```text
12345
1234
a1b a2b a3b
```

The last one surprises everyone at first: `.*` ran to the end of the text, then **backed off** one character at a time until it found a `b` to finish the match. So it matched from the first `a` to the **last** `b`. Section 9 is devoted to this behaviour and how to control it.

### 5.3 The zero-width trap of `*`

`*` and `?` can match **zero** times. A pattern made only of such items can match the **empty string**, and it will, everywhere:

```python
import re

print(re.findall(r"\d*", "ab12c"))
print(re.search(r"\d*", "ab12c"))
print(re.findall(r"\d+", "ab12c"))
```
```text
['', '', '12', '', '']
<re.Match object; span=(0, 0), match=''>
['12']
```

`re.search(r"\d*", "ab12c")` succeeds at position 0 with an **empty** match: zero digits is "0 or more digits". The search never reaches `12`. When you mean "at least one", write `+`. A pattern that can match empty is almost always a bug.

### 5.4 Anchors: `^`, `$`, `\A`, `\Z`, `\b`, `\B`

An **anchor** does not match a character. It matches a **position** between characters, and it has **zero width**: it consumes nothing.

| Anchor | Matches at |
|---|---|
| `^` | the start of the text (and of every line, with `re.MULTILINE`) |
| `$` | the end of the text, **or just before a newline at the very end** (and at every line end, with `re.MULTILINE`) |
| `\A` | only the very start of the text |
| `\Z` | only the very end of the text |
| `\b` | a word boundary: a word character on one side, a non-word character (or the edge of the text) on the other |
| `\B` | any position that is **not** a word boundary |

```python
import re

print(re.findall(r"^\w+", "first second third"))
print(re.findall(r"\w+$", "first second third"))
print(re.findall(r"\bcat\b", "cat catalog bobcat cat."))
print(re.findall(r"\Bcat\B", "cat catalog bobcat concatenate"))
```
```text
['first']
['third']
['cat', 'cat']
['cat']
```

`\bcat\b` is the standard way to find the **whole word** `cat` and not the `cat` inside `catalog` or `bobcat`. `\Bcat\B` finds `cat` only in the **middle** of a word.

Where exactly is a word boundary? Think of positions as the gaps **between** characters: position 0 is before the first character, position 1 is between the first and the second, and so on. In `"hi, you"` the characters are `h`(0) `i`(1) `,`(2) space(3) `y`(4) `o`(5) `u`(6), and the end of the text is position 7. A boundary sits wherever a word character meets a non-word character or an edge:

```python
import re

text = "hi, you"
print([m.start() for m in re.finditer(r"\b", text)])
```
```text
[0, 2, 4, 7]
```

Positions 0 and 2 surround `hi`; 4 and 7 surround `you`. Between `,` and the space there is no boundary: both are non-word characters.

### 5.5 `$` versus `\Z`: the trailing newline

Here is a subtle trap that matters for validation. `$` matches at the end, **and also just before a final `\n`**. Text read from a file or from `input()` sometimes keeps that newline:

```python
import re

for s in ["1234", "1234\n", "1234\n\n"]:
    print(repr(s),
          bool(re.search(r"^\d+$", s)),
          bool(re.search(r"\A\d+\Z", s)),
          bool(re.fullmatch(r"\d+", s)))
```
```text
'1234' True True True
'1234\n' True False False
'1234\n\n' False False False
```

`^\d+$` says `"1234\n"` is "only digits", which is false. Two safe options: `\A...\Z`, or simply `fullmatch`, which needs the pattern to cover the whole string with nothing left over. (Python 3.14 also accepts `\z` as another spelling of `\Z`, as other languages do; in Python 3.11 to 3.13, `\z` is an error. Write `\Z`, which works in every version.)

### 5.6 `^` and `$` with `re.MULTILINE`

With the `re.MULTILINE` flag, `^` and `$` also match at the start and end of **every line** inside the text. `\A` and `\Z` never change: they always mean the whole text.

```python
import re

text = "apple 3\nbanana 12\ncherry 7"
print(re.findall(r"^\w+", text))
print(re.findall(r"^\w+", text, flags=re.MULTILINE))
print(re.findall(r"\d+$", text, flags=re.MULTILINE))
print(re.findall(r"\A\w+", text, flags=re.MULTILINE))
```
```text
['apple']
['apple', 'banana', 'cherry']
['3', '12', '7']
['apple']
```

This is very handy for processing a whole file's text at once (section 11 has more on flags).

#### Try it 5.1

Predict each result.

```python
import re
print(re.findall(r"colou?r", "color colour colouur"))
print(re.findall(r"\d{3,}", "1 22 333 4444"))
print(re.findall(r"\bis\b", "This is his island; is it?"))
print(re.findall(r"go*gle", "ggle gogle google gooogle"))
print(bool(re.search(r"^ok$", "ok\n")), bool(re.fullmatch(r"ok", "ok\n")))
```

<details><summary>Answer</summary>

```text
['color', 'colour']
['333', '4444']
['is', 'is']
['ggle', 'gogle', 'google', 'gooogle']
True False
```

`colou?r` allows zero or one `u`. `\d{3,}` needs at least three digits. Only the two stand-alone words `is` count; the `is` in `This`, `his` and `island` is inside a word. `go*gle` allows any number of `o`, even zero (`ggle`). The last line is the trailing-newline trap from 5.5.

</details>

#### Try it 5.2

Predict each line. For the last one, remember that `^` is a zero-width position.

```python
import re
print(re.findall(r"\b\w", "it's a well-known fact"))
print(re.findall(r"\w+\b", "x=10; y = 20"))
print(re.sub(r"^", "> ", "one\ntwo", flags=re.MULTILINE))
print(re.findall(r"\d{2}$", "room 101\nfloor 12", flags=re.M))
```

<details><summary>Answer</summary>

```text
['i', 's', 'a', 'w', 'k', 'f']
['x', '10', 'y', '20']
> one
> two
['01', '12']
```

Line 1: a boundary sits before every first letter of a word, and the apostrophe and the hyphen also start new "words" (`s`, `k`). Line 3: `re.sub` inserted `> ` at every line start, because with MULTILINE `^` matches there and replacing an empty match inserts text. That is a neat way to quote a block of text.

</details>

## 6. `findall`, `finditer`, `split`, and validation with `fullmatch`

### 6.1 `re.findall`: every match as strings

`re.findall(pattern, text)` returns a **list** of all non-overlapping matches, scanning left to right. After each match, the search continues **after** the end of that match.

```python
import re

print(re.findall(r"\d+", "3 apples, 12 pears and 100 grapes"))
print(re.findall(r"aa", "aaaa"))
print(re.findall(r"\d+", "no digits"))
```
```text
['3', '12', '100']
['aa', 'aa']
[]
```

`"aaaa"` gives two `aa` matches, not three: matches **do not overlap**. If nothing matches, you get an empty list, never `None`.

`findall` hides one important twist: **if the pattern contains groups, it returns the groups, not the whole match.** Section 7.3 covers this; it catches everyone once.

### 6.2 `re.finditer`: Match objects, one at a time

`findall` gives only the matched strings. When you also need **positions** or **groups**, use `re.finditer`. It returns an **iterator** of Match objects (Chapter 10), so it also uses little memory on huge texts:

```python
import re

text = "Rs.250 for tea, Rs.1200 for lunch"
for m in re.finditer(r"\d+", text):
    print(m.group(), m.span())

spans = [m.span() for m in re.finditer(r"Rs\.", text)]
print(spans)
```
```text
250 (3, 6)
1200 (19, 23)
[(0, 3), (16, 19)]
```

A useful rule: **reach for `finditer` whenever you need more than the text of the match.** It is also the right choice in a loop that might stop early, since it does no work for matches you never ask for.

### 6.3 `re.split`: cut on a pattern

`str.split(",")` splits on one fixed string. `re.split` splits wherever a **pattern** matches:

```python
import re

line = "apple, banana;cherry ;  date,,fig"
print(line.split(","))
print(re.split(r"\s*[,;]\s*", line))
print([t for t in re.split(r"[,;\s]+", line) if t])
print(re.split(r"\s+", "  leading and trailing  "))
```
```text
['apple', ' banana;cherry ;  date', '', 'fig']
['apple', 'banana', 'cherry', 'date', '', 'fig']
['apple', 'banana', 'cherry', 'date', 'fig']
['', 'leading', 'and', 'trailing', '']
```

Three things to notice:

- Two separators next to each other (`,,`) produce an **empty string** between them, just like `str.split(",")`. The pattern `[,;\s]+` treats a whole run of separators as one.
- Unlike `str.split()` with no argument, `re.split(r"\s+", ...)` keeps empty strings at the ends when the text starts or ends with a separator. Filter them out, or `strip()` first.
- A pattern that can match the empty string splits between **every** character. Use `+`, not `*`.

**Split keeps groups.** If the pattern has a capturing group (section 7), the separators themselves appear in the result, between the pieces. This is perfect for a tiny calculator tokenizer:

```python
import re

print(re.split(r"[-+*/]", "12+3*45-6"))
print(re.split(r"([-+*/])", "12+3*45-6"))
print(re.split(r",", "a,b,c,d", maxsplit=2))
```
```text
['12', '3', '45', '6']
['12', '+', '3', '*', '45', '-', '6']
['a', 'b', 'c,d']
```

`maxsplit=2` stops after two cuts, leaving the rest of the text in the last piece. Write it as a keyword argument; passing it by position is deprecated since Python 3.13.

### 6.4 Validation: why `fullmatch` and not `search`

A **validator** answers "is this whole input in the right form?" The commonest regex bug in real code is to validate with `search` or `match`:

```python
import re

def bad_pin(s):
    return re.search(r"[0-9]{6}", s) is not None

def bad_pin2(s):
    return re.match(r"[0-9]{6}", s) is not None

def good_pin(s):
    return re.fullmatch(r"[0-9]{6}", s) is not None

for s in ["560001", "5600011", "PIN560001", "560001abc", "56000"]:
    print(f"{s!r:12} {bad_pin(s)!s:6} {bad_pin2(s)!s:6} {good_pin(s)}")
```
```text
'560001'     True   True   True
'5600011'    True   True   False
'PIN560001'  True   False  False
'560001abc'  True   True   False
'56000'      False  False  False
```

`search` accepts any text that **contains** six digits. `match` accepts any text that **starts with** six digits, so `"5600011"` and `"560001abc"` slip through. Only `fullmatch` gives the right answer for every row. Make it a habit: **validate with `fullmatch`.**

A full example: a college roll number of the form `BCA`, a two-digit year, a hyphen, and a three-digit number, like `BCA24-017`.

```python
import re

def valid_roll(s):
    return re.fullmatch(r"BCA[0-9]{2}-[0-9]{3}", s.strip()) is not None

for s in ["BCA24-017", " BCA24-017 ", "bca24-017", "BCA2024-017", "BCA24-17"]:
    print(f"{s!r:15} {valid_roll(s)}")
```
```text
'BCA24-017'     True
' BCA24-017 '   True
'bca24-017'     False
'BCA2024-017'   False
'BCA24-17'      False
```

Calling `strip()` first forgives spaces at the ends, a friendly choice for form input. Whether lowercase should be accepted is a **rule** of the problem, not a regex question; here it is rejected.

#### Try it 6.1

Predict each line.

```python
import re
print(re.findall(r"[A-Z][a-z]+", "Delhi and Mumbai, not mumbai or PUNE"))
print(re.split(r"-+", "a-b--c---d"))
print(re.split(r"(-+)", "a-b--c"))
print(len(re.findall(r"o", "foo boo zoo")))
print([m.start() for m in re.finditer(r"oo", "foo boo zoo")])
```

<details><summary>Answer</summary>

```text
['Delhi', 'Mumbai']
['a', 'b', 'c', 'd']
['a', '-', 'b', '--', 'c']
6
[1, 5, 9]
```

`[A-Z][a-z]+` needs a capital followed by at least one lowercase letter, so `PUNE` fails (`U` is not lowercase) and `mumbai` fails (no capital). With a group, `split` keeps the separators `-` and `--`.

</details>

## 7. Groups and alternation

### 7.1 Capturing groups: `( )`

Round brackets do two jobs at once:

1. They **group** a part of the pattern, so a quantifier or `|` applies to the whole part. `(ab)+` means "one or more `ab`".
2. They **capture** the text that part matched, so you can read it later with `m.group(1)`, `m.group(2)`, and so on.

Groups are numbered by their **opening bracket**, from left to right, starting at 1. Group 0 is always the whole match.

```python
import re

m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "Released on 2024-03-05 at noon")
print(m.group(0))
print(m.group(1), m.group(2), m.group(3))
print(m.group(1, 3))
print(m.groups())
print(m.span(2))
year, month, day = m.groups()
print(int(day), int(month), int(year))
```
```text
2024-03-05
2024 03 05
('2024', '05')
('2024', '03', '05')
(17, 19)
5 3 2024
```

`m.groups()` returns a tuple of all groups, perfect for tuple unpacking. `m.span(2)` gives the position of group 2 only. Captured text is always a **string**; convert it yourself with `int()`.

This is the heart of the first outcome of this chapter: **a pattern with groups turns unstructured text into fields.**

### 7.2 Nested and optional groups

Groups can be nested; count the **opening** brackets to know the numbers:

```python
import re

m = re.search(r"((\d+)\.(\d+))\s*(kg|g)", "weight: 12.50 kg")
print(m.groups())
print(m.group(1), "|", m.group(2), "|", m.group(3), "|", m.group(4))
```
```text
('12.50', '12', '50', 'kg')
12.50 | 12 | 50 | kg
```

If a group is optional and did not take part in the match, its value is `None`:

```python
import re

pattern = r"(\d+)(?:\.(\d+))?"
for s in ["42", "42.5"]:
    m = re.fullmatch(pattern, s)
    print(s, m.groups(), m.groups(default="0"))
```
```text
42 ('42', None) ('42', '0')
42.5 ('42', '5') ('42', '5')
```

`groups(default="0")` replaces `None` with a value you choose. The `(?:...)` in that pattern is a **non-capturing** group, explained next.

### 7.3 `findall` with groups

Remember the twist from section 6.1? Here it is:

```python
import re

text = "2024-03-05 and 2023-12-31"
print(re.findall(r"\d{4}-\d{2}-\d{2}", text))        # no groups: whole matches
print(re.findall(r"(\d{4})-\d{2}-\d{2}", text))      # one group: that group only
print(re.findall(r"(\d{4})-(\d{2})-(\d{2})", text))  # several: tuples of groups
```
```text
['2024-03-05', '2023-12-31']
['2024', '2023']
[('2024', '03', '05'), ('2023', '12', '31')]
```

The rule for `findall`:

- **no groups**: a list of whole matches;
- **one group**: a list of that group's text;
- **two or more groups**: a list of tuples.

This is convenient when you know it, and confusing when you do not. If you add brackets just to apply a quantifier, `findall` suddenly changes its output. The fix is the non-capturing group.

### 7.4 Non-capturing groups: `(?:...)`

`(?:...)` groups **without** capturing. Use it whenever you need brackets only for structure:

```python
import re

text = "hahaha! ha. hahaha"
print(re.findall(r"(ha)+", text))
print(re.findall(r"(?:ha)+", text))
```
```text
['ha', 'ha', 'ha']
['hahaha', 'ha', 'hahaha']
```

With a capturing group repeated by `+`, the group keeps only its **last** repetition, so `findall` returns `'ha'` three times. With `(?:ha)+`, there are no groups, so `findall` returns the whole matches.

A good habit: **use `( )` only for the parts you want to read back, and `(?:...)` for everything else.** Your group numbers then stay small and meaningful.

### 7.5 Alternation: `|`

The vertical bar means "**or**": `cat|dog` matches `cat` or `dog`. It has the **lowest priority** of all regex operators, so it splits the **whole** pattern (or the whole group it is in) into alternatives:

```python
import re

print(re.findall(r"cat|dog", "cat, dog, cow"))
print(re.findall(r"gr(?:a|e)y", "gray grey groy"))
print(re.fullmatch(r"jpg|png|gif", "png") is not None)
print(re.findall(r"^cat|dog$", "cat dog"))
print(re.findall(r"^(?:cat|dog)$", "cat dog"))
```
```text
['cat', 'dog']
['gray', 'grey']
True
['cat', 'dog']
[]
```

The fourth line shows the priority trap: `^cat|dog$` means "(`^cat`) or (`dog$`)", not "`^` then `cat` or `dog` then `$`". **Put alternatives inside a group** whenever anything else is in the pattern.

The engine tries alternatives **from left to right** and takes the **first** one that leads to a match, not the longest:

```python
import re

print(re.findall(r"Java|JavaScript", "JavaScript and Java"))
print(re.findall(r"JavaScript|Java", "JavaScript and Java"))
print(re.findall(r"\b(?:Java|JavaScript)\b", "JavaScript and Java"))
```
```text
['Java', 'Java']
['JavaScript', 'Java']
['JavaScript', 'Java']
```

Two fixes: put the **longer** alternative first, or add a boundary (`\b`) so a too-short alternative fails and the engine tries the next one.

### 7.6 `m.lastindex` and `m.lastgroup`

When a pattern has several alternative groups, `m.lastindex` tells you the **number** of the last group that matched. (With named groups, `m.lastgroup` gives its **name**, which section 12.6 uses to build a tokenizer.)

```python
import re

for s in ["42", "abc", "+"]:
    m = re.fullmatch(r"(\d+)|([a-z]+)|([-+*/])", s)
    print(s, m.lastindex, m.groups())
```
```text
42 1 ('42', None, None)
abc 2 (None, 'abc', None)
+ 3 (None, None, '+')
```

#### Try it 7.1

Predict each line.

```python
import re
m = re.search(r"(\w+)@(\w+)\.(com|in)", "mail ravi@example.in today")
print(m.group(0))
print(m.groups())
print(re.findall(r"(\w)(\d)", "a1 b2 cc"))
print(re.findall(r"(?:\w)(\d)", "a1 b2 cc"))
print(re.findall(r"I|In|India", "India"))
```

<details><summary>Answer</summary>

```text
ravi@example.in
('ravi', 'example', 'in')
[('a', '1'), ('b', '2')]
['1', '2']
['I']
```

With two groups `findall` gives tuples; with one capturing group (the other is non-capturing) it gives plain strings. In the last line, `I` is tried first and succeeds, so `In` and `India` are never used. After `I`, the search continues from `n`, where no alternative matches.

</details>

#### Try it 7.2

Count the brackets, then predict.

```python
import re
m = re.search(r"((a)(b(c)))(d)?", "xabcx")
print(m.groups())
print(m.group(3), m.lastindex)
print(re.findall(r"(\d)(?:-(\d))?", "1-2 3"))
print(re.search(r"(\w+) (\w+)", "hello big world").group(2))
```

<details><summary>Answer</summary>

```text
('abc', 'a', 'bc', 'c', None)
bc 1
[('1', '2'), ('3', '')]
big
```

Opening brackets from the left: 1 is `((a)(b(c)))`, 2 is `(a)`, 3 is `(b(c))`, 4 is `(c)`, 5 is the optional `(d)`, which did not take part, so it is `None`. `lastindex` is the number of the last group that **closed**: group 1, because it closes after groups 2 to 4. In `findall`, an optional group that did not match gives an empty string `''` (not `None`). The last line: the match is `hello big`, so group 2 is `big`.

</details>

## 8. Named groups and backreferences

### 8.1 Why names?

Group numbers are fragile. Add one group at the start of the pattern, and every number after it shifts; code that reads `m.group(3)` silently reads the wrong field. And `m.group(3)` tells a reader nothing. **Named groups** fix both problems.

The syntax is `(?P<name>...)`. The `P` stands for Python, which invented the syntax; other languages copied it.

```python
import re

pattern = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
m = re.search(pattern, "Due: 2024-03-05.")
print(m.group("year"), m.group("month"), m.group("day"))
print(m["day"])
print(m.groupdict())
print(m.group(1))
```
```text
2024 03 05
05
{'year': '2024', 'month': '03', 'day': '05'}
2024
```

Four ways to read the fields:

- `m.group("year")`, by name;
- `m["day"]`, the same, shorter (a Match object supports `[ ]`);
- `m.groupdict()`, a **dict** of all named groups, ready to use as data;
- the numbers still work: named groups are counted like any other.

### 8.2 From `groupdict()` to real data

`groupdict()` is the bridge from text to Python data. Here each line of a simple "key = value" settings file becomes a dict entry:

```python
import re

config = """\
# settings
name = Asha
 port=8080
debug =   true
this line is broken
"""
LINE = r"\s*(?P<key>\w+)\s*=\s*(?P<value>.*?)\s*"
settings = {}
for lineno, line in enumerate(config.splitlines(), start=1):
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    m = re.fullmatch(LINE, line)
    if m is None:
        print(f"line {lineno}: cannot parse {line!r}")
        continue
    settings[m["key"]] = m["value"]
print(settings)
```
```text
line 5: cannot parse 'this line is broken'
{'name': 'Asha', 'port': '8080', 'debug': 'true'}
```

(`.*?` is a **lazy** "anything", explained in section 9; here it lets the final `\s*` take the trailing spaces instead of the value.)

Notice the shape of the loop, which you will use again in the project: skip blank and comment lines, `fullmatch` each line, report what does not parse **with its line number**, and keep going.

Named groups also make `groupdict()` easy to combine with a dataclass, because the group names can be exactly the field names:

```python
import re
from dataclasses import dataclass

@dataclass
class Version:
    major: int
    minor: int
    patch: int

VERSION = r"v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"

def parse_version(s):
    m = re.fullmatch(VERSION, s.strip())
    if m is None:
        return None
    return Version(**{k: int(v) for k, v in m.groupdict().items()})

print(parse_version("v3.12.1"))
print(parse_version("2.0"))
```
```text
Version(major=3, minor=12, patch=1)
None
```

`Version(**d)` unpacks the dict into keyword arguments (Chapter 6). The pattern names and the dataclass fields match, so the conversion is one line.

### 8.3 Backreferences: "the same text again"

A **backreference** matches **the same text** that an earlier group already captured. `\1` means "whatever group 1 matched", `\2` group 2, and so on. With a named group, write `(?P=name)`.

The classic use is finding doubled words, a common typing mistake:

```python
import re

text = "This is is a test of the the backreference. Paris in the the spring."
print(re.findall(r"\b(\w+)\s+\1\b", text))
for m in re.finditer(r"\b(?P<word>\w+)\s+(?P=word)\b", text):
    print(m.span(), repr(m.group()))
```
```text
['is', 'the', 'the']
(5, 10) 'is is'
(21, 28) 'the the'
(53, 60) 'the the'
```

Read `\b(\w+)\s+\1\b` aloud: "a whole word, captured; some spaces; **the same word again**; a boundary". The final `\b` matters: without it, `the theory` would count, because `\1` = `the` matches the start of `theory`.

A backreference does **not** repeat the pattern; it repeats the **text**. `(\d)\1` matches `33` but not `34`, although `\d\d` matches both:

```python
import re

print(re.findall(r"(\d)\1", "11 23 44 56 99"))
print(re.findall(r"\d\d", "11 23 44 56 99"))
```
```text
['1', '4', '9']
['11', '23', '44', '56', '99']
```

### 8.4 Matching pairs: quotes and tags

Backreferences shine when the **end** must agree with the **start**. A string may be quoted with `'` or `"`, and it must close with the same quote:

```python
import re

text = """say "hello" and 'bye' but not "mixed' ones"""
for m in re.finditer(r"""(?P<q>["'])(?P<body>.*?)(?P=q)""", text):
    print(m["q"], m["body"])
```
```text
" hello
' bye
```

The third quote opens with `"` and needs a `"` to close it; the `'` after `mixed` will not do, and there is no other `"` later in the text. So no match is reported for it at all. That is correct by the rule: the text itself is broken. (The pattern is written with triple quotes, `r"""..."""`, so it may contain both kinds of quote.)

Backreferences cannot count. They check "same text", not "balanced brackets". `<(\w+)>.*?</\1>` matches a simple `<b>bold</b>`, but nested tags like `<b><b>x</b></b>` are beyond any regex; see section 13.5.

#### Try it 8.1

Predict each line.

```python
import re
print(re.findall(r"(\w)\1", "bookkeeper"))
print(re.search(r"(?P<x>\w+)-(?P=x)", "ab-ab cd-ce").group())
print(re.fullmatch(r"(\w+) \1", "hey hey") is not None)
print(re.fullmatch(r"(\w+) \1", "hey Hey") is not None)
m = re.search(r"(?P<user>\w+)@(?P<host>[\w.]+)", "to: dev@mail.example.org")
print(m.groupdict())
```

<details><summary>Answer</summary>

```text
['o', 'k', 'e']
ab-ab
True
False
{'user': 'dev', 'host': 'mail.example.org'}
```

`bookkeeper` has three doubled letters: `oo`, `kk`, `ee`. `ab-ab` matches; `cd-ce` would need `cd-cd`. A backreference is case-sensitive unless you use `re.IGNORECASE` (then `hey Hey` matches). The host class `[\w.]` includes the dot, so the whole domain is captured.

</details>

## 9. Greedy versus lazy

### 9.1 The problem with greedy

Section 5.2 showed that quantifiers are **greedy**: they take as much as they can. Most of the time that is what you want (`\d+` should take the whole number). But with `.*` it is often wrong. Try to pull the tags out of a piece of HTML-like text:

```python
import re

html = "<b>bold</b> and <i>italic</i>"
print(re.findall(r"<.*>", html))
```
```text
['<b>bold</b> and <i>italic</i>']
```

One match, the whole line, instead of four tags. Here is what the engine did, step by step, starting at position 0:

1. `<` matches the first `<`.
2. `.*` is greedy: it swallows **everything** to the end of the text: `b>bold</b> and <i>italic</i>`.
3. Now `>` must match, but there is no text left. So `.*` **gives back** one character (the final `>`), and `>` matches it.
4. The whole pattern has matched, from the first `<` to the **last** `>`.

Giving back characters and trying again is called **backtracking**. It is how every quantifier works when the rest of the pattern fails, and it is the key to section 13.

### 9.2 Lazy quantifiers: `*?`, `+?`, `??`, `{m,n}?`

Put a `?` **after** a quantifier and it becomes **lazy** (also called *non-greedy* or *reluctant*): it takes **as few** repetitions as it can, and takes one more only if the rest of the pattern fails.

| Greedy | Lazy | Lazy meaning |
|---|---|---|
| `*` | `*?` | 0 or more, as few as possible |
| `+` | `+?` | 1 or more, as few as possible |
| `?` | `??` | 0 or 1, prefer 0 |
| `{m,n}` | `{m,n}?` | m to n, as few as possible |

```python
import re

html = "<b>bold</b> and <i>italic</i>"
print(re.findall(r"<.*?>", html))
print(re.findall(r"<[^>]*>", html))
```
```text
['<b>', '</b>', '<i>', '</i>']
['<b>', '</b>', '<i>', '</i>']
```

With `.*?`, the engine tries zero characters first, then one, then two, and stops at the **first** `>` that lets the pattern finish.

The second line shows a better habit: **say what may not appear**. `[^>]*` means "any characters except `>`", so it can never run past the end of a tag. A **negated class** is usually clearer and faster than a lazy dot, because the engine never has to backtrack.

### 9.3 Lazy does not mean "shortest match"

A common misunderstanding: lazy quantifiers do **not** find the shortest possible match in the text. The engine still starts at the **leftmost** position that works. Laziness only decides how far a match extends **from that start**:

```python
import re

text = "aaab"
print(re.search(r"a+?b", text).group())
print(re.search(r"a+?", text).group())
print(re.findall(r"\d{2,4}?", "123456789"))
print(re.findall(r"\d{2,4}", "123456789"))
```
```text
aaab
a
['12', '34', '56', '78']
['1234', '5678']
```

`a+?b` still matches `aaab`: the match starts at position 0 (leftmost wins), and the lazy `a+?` grows until `b` can match. Without the `b`, `a+?` stops after one `a`. `\d{2,4}?` takes 2 digits each time; greedy `\d{2,4}` takes 4.

### 9.4 Lazy matching at the end of a pattern

A lazy quantifier at the **very end** of a pattern has nothing after it that forces it to grow, so it matches the minimum:

```python
import re

print(re.search(r"id=.*?", "id=42;").group())
print(re.search(r"id=.*?;", "id=42;").group())
print(re.search(r"id=(.*?)(?:;|$)", "id=42").group(1))
```
```text
id=
id=42;
42
```

`id=.*?` matches just `id=`, with an empty `.*?`. A lazy quantifier needs something **after** it, a delimiter like `;` or an anchor like `$`, to say where to stop.

#### Try it 9.1

Predict each list. This is the most important exercise of the chapter; trace each pattern step by step before running.

```python
import re
s = '"one" and "two"'
print(re.findall(r'".*"', s))
print(re.findall(r'".*?"', s))
print(re.findall(r'"[^"]*"', s))
print(re.findall(r"\d+?", "2024"))
print(re.findall(r"\d+?\b", "2024 7"))
```

<details><summary>Answer</summary>

```text
['"one" and "two"']
['"one"', '"two"']
['"one"', '"two"']
['2', '0', '2', '4']
['2024', '7']
```

Greedy `".*"` runs from the first quote to the last. Lazy `".*?"` stops at the first closing quote, and so does `"[^"]*"`. `\d+?` alone takes one digit per match. In the last line, `\b` forces the lazy `\d+?` to grow until a word boundary follows, so each match is a whole number.

</details>

### 9.5 Possessive quantifiers and atomic groups (Python 3.11+)

Python 3.11 added two features that turn backtracking **off** for part of a pattern. You will meet them in section 13 as a tool against slow patterns; here is what they mean.

- A **possessive** quantifier, written `*+`, `++`, `?+` or `{m,n}+`, is greedy and **never gives back** what it took.
- An **atomic group** `(?>...)` matches its contents once, the normal way, and then **locks** the result: if the rest of the pattern fails, the engine does not come back inside the group to try other choices.

```python
import re

print(re.fullmatch(r"\d+5", "12345"))
print(re.fullmatch(r"\d++5", "12345"))
print(re.fullmatch(r"(?>\d+)5", "12345"))
print(re.fullmatch(r"\d++", "12345"))
```
```text
<re.Match object; span=(0, 5), match='12345'>
None
None
<re.Match object; span=(0, 5), match='12345'>
```

`\d+5` matches because `\d+` gives back the `5`. With `\d++` it keeps all five digits, the `5` in the pattern finds nothing left, and the match fails. Possessive and atomic forms are only safe when giving back could **never** help, for example `\d++` followed by something that is **not** a digit. Section 13.4 uses exactly that idea.

These are not available in Python 3.10 or older; there, `\d++` is an error ("multiple repeat").

## 10. Lookahead and lookbehind

### 10.1 Checking without consuming

Sometimes you want to say "match `X`, but only if `Y` comes next" or "only if `Z` came before", **without** making `Y` or `Z` part of the match. **Lookaround** assertions do this. Like `\b`, they are **zero-width**: they test the text at the current position and consume nothing.

| Syntax | Name | Succeeds if... |
|---|---|---|
| `(?=...)` | positive lookahead | what follows matches `...` |
| `(?!...)` | negative lookahead | what follows does **not** match `...` |
| `(?<=...)` | positive lookbehind | what precedes matches `...` |
| `(?<!...)` | negative lookbehind | what precedes does **not** match `...` |

The arrow `<` in the lookbehind forms points backwards. The `!` means "not".

### 10.2 Lookahead

```python
import re

text = "100px 20em 35px 7%"
print(re.findall(r"\d+(?=px)", text))       # numbers followed by px
print(re.findall(r"\d+px", text))           # same, but px is in the match
print(re.findall(r"\b\d+(?!px|\d)", text))  # numbers NOT followed by px
```
```text
['100', '35']
['100px', '35px']
['20', '7']
```

Line 1 returns only the numbers: `(?=px)` checked for `px` but did not consume it. Line 3 needs care: without `\d` in the negative lookahead, `10` in `100px` would match (it is followed by `0`, not `px`). Negative lookarounds often need such extra guards; test them on tricky input.

### 10.3 Several conditions at one position: password rules

Because a lookahead consumes nothing, you can stack several at the **same** position. Each one checks a separate rule on the whole string. This is the standard regex for password rules:

```python
import re

STRONG = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)\S{8,}"

for pw in ["Secret123", "secret123", "SECRET123", "Secretabc", "Sec1", "Secret 123"]:
    print(f"{pw!r:13} {re.fullmatch(STRONG, pw) is not None}")
```
```text
'Secret123'   True
'secret123'   False
'SECRET123'   False
'Secretabc'   False
'Sec1'        False
'Secret 123'  False
```

Read it as: at the start, *look ahead* and check "somewhere there is a lowercase letter"; still at the start, check "somewhere an uppercase letter"; still at the start, check "somewhere a digit"; then actually match 8 or more non-space characters to the end (`fullmatch`).

Is this better than four simple checks in Python? Often **not**:

```python
def strong(pw):
    return (len(pw) >= 8
            and not any(c.isspace() for c in pw)
            and any(c.islower() for c in pw)
            and any(c.isupper() for c in pw)
            and any(c.isdigit() for c in pw))

print(strong("Secret123"), strong("secret123"))
```
```text
True False
```

The Python version can also tell the user **which** rule failed. Know the lookahead technique (you will see it in other people's code, and in tools that accept only one pattern), but prefer readable code when you have the choice.

### 10.4 Lookbehind

Lookbehind checks the text **before** the current position:

```python
import re

text = "Tea Rs.20, coffee ₹35, tip 10, total Rs.65"
print(re.findall(r"(?<=Rs\.)\d+", text))
print(re.findall(r"(?:(?<=Rs\.)|(?<=₹))\d+", text))
print(re.findall(r"(?<![\d.₹])\b\d+", text))
```
```text
['20', '65']
['20', '35', '65']
['10']
```

The first two lines give the amounts **without** the currency symbol in the match. The second line needs two separate lookbehinds, one for `Rs.` and one for `₹`, joined by `|`; the next section explains why a single `(?<=Rs\.|₹)` is not allowed. The third finds numbers that are **not** right after a digit, a dot or `₹`: only the tip.

### 10.5 The fixed-width rule

Python's lookbehind has one important limit: the pattern inside it must have a **fixed width**, so the engine knows exactly how many characters to step back. A quantifier like `+`, `*` or `{1,3}` breaks that rule, and so do alternatives of **different** lengths: `Rs\.` is 3 characters and `₹` is 1. (Alternatives of the **same** length, like `(?<=Rs\.|Rs:)`, are fine.)

```python
import re

for p in [r"(?<=Rs\.)\d+", r"(?<=Rs\.|Rs:)\d+", r"(?<=Rs\.|₹)\d+", r"(?<=Rs\.\s*)\d+", r"(?<=\d{1,3})x"]:
    try:
        re.compile(p)
        print(f"{p:18} ok")
    except re.error as e:
        print(f"{p:18} error: {e}")
```
```text
(?<=Rs\.)\d+       ok
(?<=Rs\.|Rs:)\d+   ok
(?<=Rs\.|₹)\d+     error: look-behind requires fixed-width pattern
(?<=Rs\.\s*)\d+    error: look-behind requires fixed-width pattern
(?<=\d{1,3})x      error: look-behind requires fixed-width pattern
```

(`re.error` is the exception for a bad pattern. Python 3.13 gave it a clearer second name, `re.PatternError`; both refer to the same class.)

Two workarounds. For alternatives of different lengths, write **one lookbehind per alternative**: `(?:(?<=Rs\.)|(?<=₹))\d+`, as in section 10.4. For a variable amount of text, **match the variable part normally and capture what you need**. Instead of `(?<=Rs\.\s*)\d+`, write `Rs\.\s*(\d+)` and read group 1:

```python
import re

text = "Rs.20, Rs. 35, Rs.   50"
print(re.findall(r"Rs\.\s*(\d+)", text))
```
```text
['20', '35', '50']
```

Lookahead has no width limit at all; only lookbehind does.

### 10.6 Lookaround as an insertion point: thousands separators

Lookarounds can match an empty **position**, and `re.sub` (section 12) can insert text there. A classic trick: put commas into a number. A comma goes at every position that is **after a digit** and **followed by a multiple of three digits up to the end**:

```python
import re

def commas(n):
    return re.sub(r"(?<=\d)(?=(?:\d{3})+$)", ",", str(n))

for n in [7, 1234, 1234567, 1000000000]:
    print(commas(n))
```
```text
7
1,234
1,234,567
1,000,000,000
```

Read the pattern as a sentence: "a position with a digit behind it, and ahead of it one or more groups of exactly three digits, then the end". No characters are consumed; `re.sub` just inserts `,` at each such position. (Indian style, 12,34,567, follows a different rule; it is a nice exercise to try. In real code, `f"{n:,}"` gives the western style directly.)

#### Try it 10.1

Predict each line.

```python
import re
print(re.findall(r"\w+(?=:)", "name: Ravi, age: 20"))
print(re.findall(r"(?<=@)\w+", "mail @ravi and @meera_k"))
print(re.findall(r"\b\w+\b(?!\()", "print(len(x)) + y"))
print(re.sub(r"(?=\d{3}$)", "-", "1800123"))
print(re.findall(r"q(?!u)", "Iraq quick qat"))
```

<details><summary>Answer</summary>

```text
['name', 'age']
['ravi', 'meera_k']
['x', 'y']
1800-123
['q', 'q']
```

Line 3 keeps the words **not** followed by `(`: `x` and `y`. Line 4 inserts a hyphen at the one position where exactly three digits remain. Line 5 finds `q` not followed by `u`, including the `q` at the very end of `Iraq`: a negative lookahead succeeds when there is nothing at all after it (compare `q[^u]` from section 4.3, which needs a character).

</details>

## 11. Flags and verbose patterns

### 11.1 What flags do

A **flag** changes how the whole pattern behaves. You pass flags as the `flags=` argument (or the third positional argument of `search`, `match`, `fullmatch`, `findall`, `finditer`, and to `re.compile`). Combine several with `|`.

| Flag | Short | Effect |
|---|---|---|
| `re.IGNORECASE` | `re.I` | letters match regardless of case |
| `re.MULTILINE` | `re.M` | `^` and `$` also match at every line start and end |
| `re.DOTALL` | `re.S` | `.` also matches newline |
| `re.VERBOSE` | `re.X` | whitespace and `#` comments in the pattern are ignored |
| `re.ASCII` | `re.A` | `\d \w \s \b` match ASCII only |

### 11.2 `IGNORECASE`, `MULTILINE`, `DOTALL`

```python
import re

text = "Error: disk\nWARNING: fan\nerror: net\nnote: ok"
print(re.findall(r"^error: \w+", text))
print(re.findall(r"^error: \w+", text, re.IGNORECASE | re.MULTILINE))
print(re.findall(r"error.*", text, re.I))
print(re.findall(r"error.*", text, re.I | re.S))
```
```text
[]
['Error: disk', 'error: net']
['Error: disk', 'error: net']
['Error: disk\nWARNING: fan\nerror: net\nnote: ok']
```

- Line 1: no flags. `^` only matches at position 0, and `Error` has a capital `E`. Nothing.
- Line 2: case is ignored and `^` matches at every line start.
- Line 3: `.*` stops at each newline.
- Line 4: with `DOTALL`, the first `.*` runs to the end of the whole text.

A common trap: passing a flag in the wrong position. `re.sub(pattern, repl, text, re.I)` passes `re.I` as `count` (the fourth parameter of `sub`), not as flags. Always write `flags=` by name for `sub`, `subn` and `split`. Since Python 3.13 the positional form gives a deprecation warning.

### 11.3 Inline flags

A flag can also be written **inside** the pattern, at the very start: `(?i)` for IGNORECASE, `(?m)` MULTILINE, `(?s)` DOTALL, `(?x)` VERBOSE, `(?a)` ASCII. You can combine letters: `(?im)`.

```python
import re

print(re.findall(r"(?i)python", "Python PYTHON python"))
print(re.findall(r"(?i:py)thon", "Python PYTHON python"))
```
```text
['Python', 'PYTHON', 'python']
['Python', 'python']
```

The second form, `(?i:...)`, applies the flag **only inside that group**: `py` may be any case, `thon` must be lowercase. A global inline flag like `(?i)` must be at the very start of the pattern; elsewhere it is an error.

Inline flags are useful when a pattern is stored as **text**, for example in a configuration file, where you cannot pass a `flags=` argument.

### 11.4 `VERBOSE`: patterns you can read

Long patterns turn into line noise. With `re.VERBOSE`, the pattern may span many lines; **whitespace is ignored** and **`#` starts a comment** until the end of the line. Here is a date-time pattern written both ways:

```python
import re

COMPACT = r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?"

VERBOSE = re.compile(r"""
    (?P<year>\d{4}) - (?P<month>\d{2}) - (?P<day>\d{2})   # date: 2024-03-05
    [T\ ]                                                 # 'T' or a space
    (?P<hour>\d{2}) : (?P<minute>\d{2})                   # time: 10:42
    (?: : (?P<second>\d{2}) )?                            # optional :17
""", re.VERBOSE)

s = "2024-03-05 10:42"
print(re.fullmatch(COMPACT, s).groups())
print(VERBOSE.fullmatch(s).groupdict())
print(VERBOSE.fullmatch("2024-03-05T10:42:17")["second"])
```
```text
('2024', '03', '05', '10', '42', None)
{'year': '2024', 'month': '03', 'day': '05', 'hour': '10', 'minute': '42', 'second': None}
17
```

Both patterns match the same strings. Only one can be read, reviewed and changed safely six months later.

Rules for verbose mode:

- A **real space** must be written as `\ `, `[ ]` or `\s`. Above, `[T\ ]` means "a `T` or a space". (This is also why `re.escape` escapes spaces.)
- A **real `#`** must be written as `\#` or `[#]`.
- Inside a character class, whitespace is kept as written, but escaping it anyway is clearer.
- Use a triple-quoted raw string, `r"""..."""`.

**Rule of thumb: once a pattern has more than about three groups, or you need to explain it to a reader, write it in verbose mode with named groups.**

### 11.5 `ASCII`

`re.ASCII` makes `\d`, `\w`, `\s` and `\b` follow ASCII rules (section 4.5):

```python
import re

print(re.findall(r"\w+", "café ४५"))
print(re.findall(r"\w+", "café ४५", re.ASCII))
```
```text
['café', '४५']
['caf']
```

#### Try it 11.1

Predict each line.

```python
import re
t = "Cat\ncat\nCAT dog"
print(len(re.findall(r"cat", t, re.I)))
print(re.findall(r"^c\w+$", t, re.I | re.M))
print(re.findall(r"(?m)^\w", t))
print(re.search(r"Cat.cat", t) is None, re.search(r"Cat.cat", t, re.S) is not None)
print(re.fullmatch(r"""\d+  # some digits
                        [a-z]  # a letter""", "12x", re.X) is not None)
```

<details><summary>Answer</summary>

```text
3
['Cat', 'cat']
['C', 'c', 'C']
True True
True
```

Line 2: with MULTILINE, `$` matches at each line end, so `Cat` and `cat` qualify, but `CAT dog` does not (`\w+` stops at the space, and `$` is not there). Line 4: the dot needs DOTALL to match the newline between `Cat` and `cat`. Line 5: in verbose mode the spaces and comments vanish, leaving `\d+[a-z]`.

</details>

## 12. `re.sub`, `re.subn` and compiled patterns

### 12.1 Replacing with `re.sub`

`re.sub(pattern, repl, text)` returns a **new** string in which every match is replaced by `repl`. (Strings are immutable, so the original is unchanged.) `re.subn` does the same and also returns **how many** replacements it made.

```python
import re

text = "Call 98450 12345 or 98450-67890 today"
print(re.sub(r"\d", "#", text))
print(re.sub(r"\s+", " ", "too    many\n\n spaces\there"))
print(re.subn(r"\d{5}[ -]?\d{5}", "<phone>", text))
print(re.sub(r"\d", "#", text, count=3))
```
```text
Call ##### ##### or #####-##### today
too many spaces here
('Call <phone> or <phone> today', 2)
Call ###50 12345 or 98450-67890 today
```

`count=3` stops after three replacements. `subn` returns a tuple `(new_text, number)`, handy for reports like "censored 3 words".

### 12.2 Backreferences in the replacement

The replacement string can use the groups of each match:

| In `repl` | Inserts |
|---|---|
| `\1`, `\2`, ... | the text of group 1, 2, ... |
| `\g<1>` | group 1 (safe when a digit follows) |
| `\g<name>` | a named group |
| `\g<0>` | the whole match |

```python
import re

print(re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\3-\2-\1", "Born 05/03/2004, joined 17/08/2022"))
print(re.sub(r"(?P<last>\w+), (?P<first>\w+)", r"\g<first> \g<last>", "Sharma, Priya"))
print(re.sub(r"\d+", r"[\g<0>]", "room 12, floor 3"))
print(re.sub(r"(\d)", r"\g<1>0", "1 2 3"))
```
```text
Born 2004-03-05, joined 2022-08-17
Priya Sharma
room [12], floor [3]
10 20 30
```

The last line shows why `\g<1>` exists: `\10` would mean "group 10". Write the replacement as a **raw string** too, for the same reasons as the pattern.

### 12.3 A function as the replacement

When the new text must be **computed**, pass a function instead of a string. `re.sub` calls it with each Match object and uses the string it returns:

```python
import re

def double(m):
    return str(int(m.group()) * 2)

print(re.sub(r"\d+", double, "3 apples and 12 pears"))
print(re.sub(r"\b\w", lambda m: m.group().upper(), "the quick brown fox"))

prices = {"tea": 20, "coffee": 35}
print(re.sub(r"\{(\w+)\}", lambda m: str(prices.get(m[1], m[0])), "tea {tea}, coffee {coffee}, cake {cake}"))
```
```text
6 apples and 24 pears
The Quick Brown Fox
tea 20, coffee 35, cake {cake}
```

The function **must return a string** (hence `str(...)`). The last example is a tiny template engine: known keys are replaced, unknown ones (`{cake}`) are left as they were by returning the whole match `m[0]`.

This is one of the most useful tools in the chapter. Anything you can compute in Python, you can do to every match in one line.

### 12.4 Empty matches in `sub`

A pattern that can match the empty string also matches **between** characters, and `sub` replaces those empty matches too:

```python
import re

print(re.sub(r"x*", "-", "abxc"))
print(re.sub(r"x+", "-", "abxc"))
```
```text
-a-b--c-
ab-c
```

This is the zero-width trap from section 5.3 again. It is useful when you mean it (section 10.6 inserted commas at empty positions), and a bug when you do not.

#### Try it 12.2

Write `mask_cards(text)` that hides every card number written as four groups of four digits, separated by single spaces or hyphens, keeping only the last four digits: `4111 1111 1111 1234` becomes `**** **** **** 1234`. The separators must be kept as they were. Test it on `"Paid with 4111-1111-1111-1234, refund to 5500 0000 0000 0004."`

<details><summary>Answer</summary>

One way: capture the last group, and replace every digit before it in a function.

```python
import re

CARD = re.compile(r"\b(\d{4}[ -]\d{4}[ -]\d{4}[ -])(\d{4})\b")

def mask_cards(text):
    return CARD.sub(lambda m: re.sub(r"\d", "*", m[1]) + m[2], text)

print(mask_cards("Paid with 4111-1111-1111-1234, refund to 5500 0000 0000 0004."))
print(mask_cards("Order 1234 5678 is not a card"))
```

```text
Paid with ****-****-****-1234, refund to **** **** **** 0004.
Order 1234 5678 is not a card
```

The replacement function itself uses `re.sub` on group 1 only, which keeps its separators. Short numbers do not have four groups, so they are left alone.

</details>

### 12.5 Compiling patterns

`re.compile(pattern, flags)` turns a pattern into a **Pattern object** once. The object has the same methods as the module, without the pattern argument:

```python
import re

DATE = re.compile(r"(?P<d>\d{2})/(?P<m>\d{2})/(?P<y>\d{4})")
print(DATE)
print(DATE.pattern, DATE.groups, DATE.groupindex)
print(DATE.search("on 05/03/2024").groupdict())
print(DATE.findall("05/03/2024 and 17/08/2022"))
print(DATE.sub(r"\g<y>-\g<m>-\g<d>", "on 05/03/2024"))
```
```text
re.compile('(?P<d>\\d{2})/(?P<m>\\d{2})/(?P<y>\\d{4})')
(?P<d>\d{2})/(?P<m>\d{2})/(?P<y>\d{4}) 3 {'d': 1, 'm': 2, 'y': 3}
{'d': '05', 'm': '03', 'y': '2024'}
[('05', '03', '2024'), ('17', '08', '2022')]
on 2024-03-05
```

Why compile?

- **Readability and reuse.** A pattern with a good name, `DATE`, `EMAIL_RE`, `LOG_LINE`, defined once at the top of the module, documents itself and is used the same way everywhere.
- **Flags travel with the pattern.** `re.compile(..., re.VERBOSE | re.IGNORECASE)` cannot be forgotten at one call site.
- **Speed, a little.** The `re` module keeps an internal **cache** of recently used patterns (a few hundred), so calling `re.search(r"...", s)` in a loop does not recompile every time. Compiling yourself skips even the cache lookup:

```python
import re
import timeit

lines = ["2024-03-05 ok", "no date here"] * 500
PAT = re.compile(r"\d{4}-\d{2}-\d{2}")

t_module = timeit.timeit(lambda: [re.search(r"\d{4}-\d{2}-\d{2}", s) for s in lines], number=50)
t_compiled = timeit.timeit(lambda: [PAT.search(s) for s in lines], number=50)
print(f"module-level: {t_module:.3f} s")
print(f"compiled:     {t_compiled:.3f} s")
```
```text
module-level: 0.030 s
compiled:     0.013 s
```

(Timings are machine-specific.) The difference is real but small. The main reasons to compile are names and flags, not speed. Do **not** compile inside the loop (`re.compile(...)` on every line); that defeats the purpose.

Pattern methods accept two extra arguments the module functions do not: `pos` and `endpos`, to search only part of the string. `PAT.search(text, 10)` starts looking at index 10. Note that `^` still means the real start of the text, not `pos`; use `PAT.match(text, pos)` to anchor at `pos`.

### 12.6 A tokenizer with named alternatives

Combining everything so far: a **tokenizer** breaks text into labelled pieces, the first step of any calculator, compiler or query language. Write one named group per kind of token, join them with `|`, and ask each match which group matched with `m.lastgroup`:

```python
import re

TOKEN = re.compile(r"""
    (?P<NUMBER> \d+(?:\.\d+)? )
  | (?P<NAME>   [A-Za-z_]\w* )
  | (?P<OP>     [-+*/=()] )
  | (?P<SKIP>   \s+ )
  | (?P<ERROR>  . )
""", re.VERBOSE)

def tokens(text):
    for m in TOKEN.finditer(text):
        kind = m.lastgroup
        if kind == "SKIP":
            continue
        if kind == "ERROR":
            raise ValueError(f"unexpected {m.group()!r} at {m.start()}")
        yield kind, m.group()

print(list(tokens("area = 3.14 * r*r")))
try:
    print(list(tokens("x = 5 $ 2")))
except ValueError as e:
    print("ValueError:", e)
```
```text
[('NAME', 'area'), ('OP', '='), ('NUMBER', '3.14'), ('OP', '*'), ('NAME', 'r'), ('OP', '*'), ('NAME', 'r')]
ValueError: unexpected '$' at 6
```

Three ideas make this work. The alternatives are tried **in order**, so `NUMBER` gets the chance before `ERROR`. The last alternative, `.`, catches **any** character the others do not, so nothing is silently skipped. And `tokens` is a **generator** (Chapter 10): it yields one token at a time.

#### Try it 12.1

Predict each line.

```python
import re
print(re.sub(r"(\w+)@(\w+)", r"\2 at \1", "ravi@home"))
print(re.sub(r"a|e", lambda m: m.group().upper(), "banana tree"))
print(re.subn(r"\s+", " ", " a  b   c "))
print(re.sub(r"(?i)\bthe\b", "a", "The cat and the theme"))
print(re.sub(r"(\d+)", r"<\1>", "1+22=23"))
```

<details><summary>Answer</summary>

```text
home at ravi
bAnAnA trEE
(' a b c ', 4)
a cat and a theme
<1>+<22>=<23>
```

Line 3: each run of spaces becomes one space, including the runs at the two ends; there were 4 runs. Line 4: `\b` keeps `theme` safe, and `(?i)` makes `The` match too.

</details>

## 13. Catastrophic backtracking, and when not to use regex

### 13.1 A pattern that takes forever

This section is about the second outcome of the chapter: **explain why a pattern is slow and rewrite it**. Start with a pattern that looks harmless: `(a+)+$`, "one or more groups of one or more `a`, then the end". On a string of `a`s it is instant. Now add one character that makes the match **fail** at the end, and time it for growing lengths:

```python
import re
import time

SLOW = re.compile(r"(a+)+$")
for n in [16, 18, 20, 22, 24]:
    text = "a" * n + "!"
    start = time.perf_counter()
    result = SLOW.match(text)
    elapsed = time.perf_counter() - start
    print(f"n={n}  result={result}  {elapsed:.3f} s")
```
```text
n=16  result=None  0.004 s
n=18  result=None  0.014 s
n=20  result=None  0.055 s
n=22  result=None  0.220 s
n=24  result=None  0.879 s
```

(Timings are machine-specific; the pattern of growth is not.) Every **two** extra characters make it about **four times** slower: the time roughly **doubles per character**. Continue the table: at n = 30 it takes about a minute, at n = 40 about a day, at n = 60 longer than a human life. The input is 61 characters long.

This is called **catastrophic backtracking**, and it is not a toy problem. Real websites have gone down because one regex met one unlucky input; attackers even send such inputs on purpose (a "ReDoS", regular expression denial of service). Python's `re` has **no timeout**: once a call starts, it runs until it finishes.

### 13.2 Why it happens

Remember how the engine works (sections 5.2 and 9.1): when the rest of the pattern fails, a quantifier **gives back** a character and the engine tries again. Normally there are only a few choices to try. In `(a+)+`, there are **many ways to cut the same string of `a`s into groups**:

```text
aaaa  as one group:     (aaaa)
      as two groups:    (aaa)(a)  (aa)(aa)  (a)(aaa)
      as three groups:  (aa)(a)(a)  (a)(aa)(a)  (a)(a)(aa)
      as four groups:   (a)(a)(a)(a)
```

That is 8 ways for 4 letters. Each extra `a` doubles the count: n letters can be cut in 2^(n-1) ways. When the input ends with `!`, `$` fails after **every** way of cutting, so the engine dutifully tries **all of them**, and then tries again from the next start position. Nothing is wrong with the engine; the pattern simply asks it to.

You can count the ways yourself with a small function that mimics the engine's choices:

```python
def ways(n):
    """How many ways can n letters be cut into groups of one or more?"""
    if n == 0:
        return 1
    return sum(ways(n - first) for first in range(1, n + 1))

print([ways(n) for n in range(1, 11)])
```
```text
[1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
```

The warning sign is always the same: **a quantifier inside a quantifier, where both can match the same characters.** The inner `a+` and the outer `( )+` compete for the same `a`s, and every split between them is a separate path for the engine.

### 13.3 Spotting dangerous patterns

Real slow patterns are rarely as obvious as `(a+)+`. Here are the shapes to look for:

| Dangerous shape | Why | Example from real code |
|---|---|---|
| `(x+)+`, `(x*)*`, `(x+)*` | nested quantifiers over the same characters | `(\d+)+`, `(\w+)*` |
| `(x+y?)+` | the optional `y` lets the groups split anywhere | `(\w+\s?)+$` ("words with optional spaces") |
| `(a\|a)+`, `(\w\|\d)+` | overlapping alternatives: one character, several ways to match | `(\w\|\d)+`: a digit is also a word character |
| `.*.*`, `.*x.*y.*` on long lines with no match | several unbounded quantifiers over the same characters | `.*=.*;.*` |

The second shape is the most common in real life. "One or more words, each followed by an optional space, up to the end" sounds reasonable:

```python
import re
import time

SLOW = re.compile(r"^(\w+\s?)+$")
for n in [16, 20, 22]:
    text = "a" * n + "!"
    start = time.perf_counter()
    SLOW.match(text)
    print(f"n={n}  {time.perf_counter() - start:.3f} s")
```
```text
n=16  0.007 s
n=20  0.100 s
n=22  0.445 s
```

Because the space is optional, `aaaa` can be split into "words" in all the same ways as before. The input does not even need spaces to trigger it.

**How to test a pattern you suspect:** time it on a long string that **almost** matches and then fails at the very end, like the `"a" * n + "!"` above. Start small (n = 10, 15, 20) and watch whether the time doubles. Never start with a big n: you may have to kill the program.

#### Try it 13.1

For each pattern, say whether it is at risk of catastrophic backtracking, and why.

1. `^\d+$`
2. `^(\d+)*$`
3. `^[a-z]+@[a-z]+\.com$`
4. `^(\w+\.?)+@example\.com$`
5. `^(?:ab|cd)+$`

<details><summary>Answer</summary>

1. Safe: one quantifier, nothing to share characters with.
2. Dangerous: nested quantifiers over the same digits, exactly the `(a+)+` shape.
3. Safe: each `+` is followed by a character (`@`, `.`) its class cannot match, so there is only one way to split the text.
4. Dangerous: the dot is optional, so `\w+` groups can split a long name in exponentially many ways when the domain does not match.
5. Safe: `ab` and `cd` cannot overlap. Each position has at most one choice.

</details>

### 13.4 Rewriting slow patterns

There are four standard repairs. They all have the same goal: **make sure each character can be matched in only one way.**

**Repair 1: remove the nesting.** `(a+)+$` matches exactly the same strings as `a+$`. The outer group added nothing but paths.

**Repair 2: make the separator required.** "Words with optional spaces" really means "a word, then any number of (space, word)": `^\w+(?:\s\w+)*$`. Now a space **must** appear between two groups, so a run of letters can only be split one way.

**Repair 3: use precise classes so neighbours cannot overlap.** In `".*"`, `.` can also match the quote, so the engine has choices. In `"[^"]*"`, it does not.

**Repair 4 (Python 3.11+): make the part possessive or atomic**, so it never gives anything back: `(\w+\s?)++$` or `(?>(\w+\s?)+)$`. This is a quick fix, but it only works when giving back could never have helped; repairs 1 to 3 are clearer.

Let us check that the rewrites match the **same strings** as the original, and are fast:

```python
import re
import time

SLOW = re.compile(r"^(\w+\s?)+$")
SAFE = re.compile(r"^\w+(?:\s\w+)*\s?$")
POSSESSIVE = re.compile(r"^(?:\w+\s?)++$")

samples = ["hello", "hello world", "hello world ", "a b c", "", " lead", "two  spaces", "end!"]
for s in samples:
    a, b, c = (bool(p.match(s)) for p in (SLOW, SAFE, POSSESSIVE))
    print(f"{s!r:15} {a!s:6} {b!s:6} {c}")

text = "a" * 5000 + "!"
for name, p in [("SAFE", SAFE), ("POSSESSIVE", POSSESSIVE)]:
    start = time.perf_counter()
    p.match(text)
    print(f"{name}: n=5000 in {time.perf_counter() - start:.4f} s")
```
```text
'hello'         True   True   True
'hello world'   True   True   True
'hello world '  True   True   True
'a b c'         True   True   True
''              False  False  False
' lead'         False  False  False
'two  spaces'   False  False  False
'end!'          False  False  False
SAFE: n=5000 in 0.0003 s
POSSESSIVE: n=5000 in 0.0000 s
```

All three agree on every sample (note the original allowed one space at the end, so the rewrite must too: `\s?$`). And on an input 5,000 characters long, the safe versions answer instantly, where the slow one would need longer than the age of the universe. (Timings are machine-specific.)

The habit to take away: **when you rewrite a pattern, keep a list of test strings, including tricky ones, and check that old and new agree on all of them.** That is the only way to know a rewrite did not change the meaning.

#### Try it 13.2

The pattern `^(\d+,?)+$` is meant to accept a comma-separated list of numbers like `1,22,333`. It hangs on `"1111111111111111111111111x"`. Rewrite it so it accepts the same strings, then check with a few samples.

<details><summary>Answer</summary>

The comma is optional, so the digits can be cut into groups in exponentially many ways. Make the comma required **between** numbers, and allow one at the end as the original did:

```python
import re
OLD = re.compile(r"^(\d+,?)+$")
NEW = re.compile(r"^\d+(?:,\d+)*,?$")
for s in ["1", "1,22,333", "1,22,", ",1", "1,,2", "12a"]:
    print(f"{s!r:11} {bool(OLD.match(s))!s:6} {bool(NEW.match(s))}")
```

```text
'1'         True   True
'1,22,333'  True   True
'1,22,'     True   True
',1'        False  False
'1,,2'      False  False
'12a'       False  False
```

</details>

### 13.5 When not to use regex

Regex describes **flat** patterns: sequences, choices and repetitions. It cannot count, and so it cannot follow **nesting**. And for many formats, a proper parser already exists in the standard library. Use the right tool:

| Data | Do not | Do |
|---|---|---|
| JSON | pick values out with regex | `json.loads` (Chapter 12) |
| CSV with quotes | `split(",")` or a regex | the `csv` module |
| HTML / XML | `<.*?>` patterns | `html.parser`, `xml.etree.ElementTree` |
| Nested brackets | a regex | a loop with a counter, or a stack |
| Dates | a regex that checks "31 February" | `datetime.strptime` (Chapter 17) |
| Simple splits / fixed text | regex | `str.split`, `in`, `startswith`, `replace` |
| File paths | regex on `/` | `pathlib` |

**Nesting.** Is every bracket matched? A regex cannot answer this for any depth, because it would need to remember how many brackets are open. A loop with a counter can:

```python
def balanced(text):
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0

for t in ["(a(b)c)", "((x)", "())(", "f(g(h(i)))"]:
    print(f"{t:12} {balanced(t)}")
```
```text
(a(b)c)      True
((x)         False
())(         False
f(g(h(i)))   True
```

**HTML.** A regex for tags breaks on attributes containing `>`, on comments, on nesting. `html.parser` handles all of that. You subclass `HTMLParser` (Chapter 14) and receive one call per tag:

```python
from html.parser import HTMLParser

class LinkFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs).get("href"))

page = '<p>See <a href="/docs?x=1&amp;y=2" title="a > b">docs</a> and <!-- <a href="old"> --> <A HREF="/faq">FAQ</A></p>'
finder = LinkFinder()
finder.feed(page)
print(finder.links)
```
```text
['/docs?x=1&y=2', '/faq']
```

The parser understood the `>` inside the attribute, skipped the commented-out link, accepted uppercase tags and decoded `&amp;`. A quick regex would get at least two of those wrong.

**JSON.** Values can contain quotes, escapes and nested objects. `json.loads` gives you real Python data in one call; never pick JSON apart with `re`.

**Regex is the right tool** for **flat, line-shaped** text with a known format: log lines, identifiers, codes, dates inside prose, configuration lines, simple tokens. That is the job of the project in the next section.

## 14. Project: a log analyser

### 14.1 The goal

The module project is a **log analyser**: a program that reads a log file, turns each line into a structured record, and summarises what happened. This is the first outcome of the chapter in action: **extract structured fields from messy text with named groups.** The problem set ends with the full version; here you will build a smaller one, with a simpler log format, step by step.

Our log lines look like this:

```text
[10:42:17] ERROR payments: card declined user=asha ms=812
```

Each line has four fields: a **time** in square brackets, a **level** (`DEBUG`, `INFO`, `WARNING`, `ERROR`), a **source** (the part of the program that wrote it) followed by a colon, and a free-text **message**. Real logs are messy, so the file will also contain blank lines, a line cut off half-way, a line with an unknown level and a stack trace line.

The plan:

1. Write one **verbose pattern with named groups** for a line.
2. Write `parse_line(line) -> Entry | None`, returning a **dataclass**.
3. Read the file lazily, line by line, remembering **line numbers** of bad lines.
4. **Summarise** with `Counter`.
5. Pull extra `key=value` fields out of the message with a second pattern.

### 14.2 The pattern

Write the pattern piece by piece, in verbose mode, with a comment per piece:

```python
LINE = re.compile(r"""
    \[ (?P<time> \d{2}:\d{2}:\d{2} ) \]        # [10:42:17]
    \s+
    (?P<level> DEBUG|INFO|WARNING|ERROR )      # one of four known levels
    \s+
    (?P<source> [a-z][a-z0-9_.]* ) :           # payments:  (module-like name)
    \s*
    (?P<message> .*? )                         # the rest, without trailing spaces
    \s*
""", re.VERBOSE)
```

Decisions worth noticing:

- `\[` and `\]` escape the brackets: they are literal characters here.
- The level is an **alternation of the known values**, not `\w+`. An unknown level like `FATAL` should fail and be reported, not slip in.
- The source uses a precise class; the colon after it is a required separator. Because `[a-z0-9_.]` cannot match `:`, there is exactly one way to split there (section 13.4).
- The message is lazy `.*?` followed by `\s*`, so trailing spaces are not part of it (we will use `fullmatch`, which forces the pattern to reach the end).

### 14.3 Parsing a line into a dataclass

```python
import re
from dataclasses import dataclass

LINE = re.compile(r"""
    \[ (?P<time> \d{2}:\d{2}:\d{2} ) \]
    \s+
    (?P<level> DEBUG|INFO|WARNING|ERROR )
    \s+
    (?P<source> [a-z][a-z0-9_.]* ) :
    \s*
    (?P<message> .*? )
    \s*
""", re.VERBOSE)

@dataclass
class Entry:
    time: str
    level: str
    source: str
    message: str

def parse_line(line: str) -> Entry | None:
    m = LINE.fullmatch(line.strip())
    if m is None:
        return None
    return Entry(**m.groupdict())

print(parse_line("[10:42:17] ERROR payments: card declined user=asha ms=812"))
print(parse_line("[10:42:18] INFO  web.api:   GET /home   \n"))
print(parse_line("[10:42:19] FATAL core: out of memory"))
print(parse_line("[10:42:"))
print(parse_line(""))
```
```text
Entry(time='10:42:17', level='ERROR', source='payments', message='card declined user=asha ms=812')
Entry(time='10:42:18', level='INFO', source='web.api', message='GET /home')
None
None
None
```

The function has a clear contract: **an `Entry` for a good line, `None` for anything else**. It never raises on bad input, because bad input is **normal** in log files. The group names equal the dataclass field names, so `Entry(**m.groupdict())` builds the object in one line (section 8.2).

### 14.4 Reading the file and keeping line numbers

A log file can be huge, so read it **lazily**: iterate over the open file (Chapter 12) instead of calling `read()`. A **generator** (Chapter 10) keeps the reading separate from the analysis. It yields `(line_number, entry_or_None)` pairs, so the caller can report bad lines precisely.

This example writes a small sample log into a temporary folder first, so it can run anywhere:

```python
import re
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

LINE = re.compile(r"""
    \[ (?P<time> \d{2}:\d{2}:\d{2} ) \] \s+
    (?P<level> DEBUG|INFO|WARNING|ERROR ) \s+
    (?P<source> [a-z][a-z0-9_.]* ) : \s*
    (?P<message> .*? ) \s*
""", re.VERBOSE)

@dataclass
class Entry:
    time: str
    level: str
    source: str
    message: str

def parse_line(line):
    m = LINE.fullmatch(line.strip())
    return Entry(**m.groupdict()) if m else None

def read_log(path):
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if line.strip():                       # skip blank lines silently
                yield lineno, parse_line(line)

SAMPLE = """\
[10:42:15] INFO web.api: GET /home user=asha ms=35
[10:42:16] DEBUG db: query ok ms=4
[10:42:17] ERROR payments: card declined user=asha ms=812

[10:42:18] WARNING web.api: slow response ms=1450
[10:42:19] ERROR payments: gateway timeout ms=5000
[10:42:20] FATAL core: out of memory
    at core.alloc (core.py:88)
[10:42:21] ERROR db: connection lost
[10:42:2
[10:42:22] INFO web.api: GET /cart user=ravi ms=41
"""

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "app.log"
    path.write_text(SAMPLE, encoding="utf-8")

    levels = Counter()
    errors_by_source = Counter()
    bad_lines = []
    for lineno, entry in read_log(path):
        if entry is None:
            bad_lines.append(lineno)
            continue
        levels[entry.level] += 1
        if entry.level == "ERROR":
            errors_by_source[entry.source] += 1

print("levels:", dict(levels))
print("errors by source:", errors_by_source.most_common())
print("unparsed lines:", bad_lines)
```
```text
levels: {'INFO': 2, 'DEBUG': 1, 'ERROR': 3, 'WARNING': 1}
errors by source: [('payments', 2), ('db', 1)]
unparsed lines: [7, 8, 10]
```

Read the result against the sample:

- Line 4 is blank: skipped, not counted as bad.
- Line 7 (`FATAL`) has an unknown level, line 8 is a stack-trace line, line 10 was cut off: all three are reported **by number**, so a person can look at them.
- `Counter` (Chapter 17) does the counting; `most_common()` sorts sources by error count.

Notice also what the analyser does **not** do: it does not crash on the first bad line, and it does not silently drop bad lines either. Both are common in quick scripts, and both hide problems.

### 14.5 Extracting extra fields from the message

Many messages carry `key=value` pairs (`user=asha ms=812`). A second, small pattern pulls them out, and `findall` with **two groups** returns `(key, value)` tuples (section 7.3), ready for `dict()`:

```python
import re

KV = re.compile(r"(\w+)=(\S+)")

for msg in ["card declined user=asha ms=812", "GET /home user=ravi ms=35", "connection lost"]:
    fields = dict(KV.findall(msg))
    print(fields)

slow = [int(ms) for msg in ["ms=35", "ms=1450", "ms=5000", "ms=41"]
        for ms in re.findall(r"\bms=(\d+)", msg) if int(ms) >= 1000]
print("slow requests (ms):", slow)
```
```text
{'user': 'asha', 'ms': '812'}
{'user': 'ravi', 'ms': '35'}
{}
slow requests (ms): [1450, 5000]
```

This two-level design, one pattern for the **line structure** and a second for the **inside of a field**, keeps each pattern small and testable. Trying to capture everything in one giant pattern makes it unreadable and, as section 13 showed, sometimes slow.

### 14.6 Design notes for the full version

The full log analyser in the problem set works the same way, with more to handle. When you write it, keep these points in mind:

- **Test `parse_line` first**, on good lines, each kind of bad line and edge cases (extra spaces, empty message), before writing the summary.
- **Several line formats?** Write one compiled pattern per format and try them in order; return the first match. Do not merge them into one huge alternation.
- **Normalise as you parse.** If one format writes `warn` and another `WARNING`, convert both to one spelling inside `parse_line`, so the rest of the program sees one vocabulary.
- **Summaries are plain Python.** Once lines are dataclasses, counting, grouping and sorting use the tools from Chapters 5 and 17; no regex is needed after parsing.
- **Ties.** If a summary asks for the "top 3", decide how equal counts are ordered and sort explicitly, for example `sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))`.

#### Try it 14.1

Using the `parse_line` from section 14.3, predict which of these lines parse, and for those that do, the `source` and `message`.

```python
"[09:00:00] INFO auth: login ok"
"[09:00:00] info auth: login ok"
"[09:00:00] INFO Auth: login ok"
"[09:00:00] WARNING  cache.v2:"
"[9:00:00] INFO auth: login ok"
"  [09:00:00] ERROR auth: bad password   "
```

<details><summary>Answer</summary>

```python
import re
from dataclasses import dataclass

LINE = re.compile(r"""
    \[ (?P<time> \d{2}:\d{2}:\d{2} ) \] \s+
    (?P<level> DEBUG|INFO|WARNING|ERROR ) \s+
    (?P<source> [a-z][a-z0-9_.]* ) : \s*
    (?P<message> .*? ) \s*
""", re.VERBOSE)

@dataclass
class Entry:
    time: str
    level: str
    source: str
    message: str

def parse_line(line):
    m = LINE.fullmatch(line.strip())
    return Entry(**m.groupdict()) if m else None

for line in ["[09:00:00] INFO auth: login ok", "[09:00:00] info auth: login ok",
             "[09:00:00] INFO Auth: login ok", "[09:00:00] WARNING  cache.v2:",
             "[9:00:00] INFO auth: login ok", "  [09:00:00] ERROR auth: bad password   "]:
    e = parse_line(line)
    print(None if e is None else (e.source, e.message))
```

```text
('auth', 'login ok')
None
None
('cache.v2', '')
None
('auth', 'bad password')
```

Lowercase `info` and capital `Auth` fail because the pattern is case-sensitive. An empty message is allowed (`.*?` can be empty). `9:00:00` fails because the hour needs two digits. Surrounding spaces are removed by `strip()` and by the final `\s*`.

</details>

#### Try it 14.2

Extend the analyser of section 14.4 so that it also reports, for each source, the **average** `ms` value over the lines that have one. Use the `KV` pattern of section 14.5 and a `defaultdict(list)`. (No answer is given: run your version on the sample and check the numbers by hand. For `web.api` you should get the average of 35, 1450 and 41.)

## 15. Common traps and summary

### 15.1 Common traps

1. **Forgetting the `r` prefix.** `"\bword\b"` contains backspace characters and silently matches nothing. Write every pattern as `r"..."`.
2. **Calling `.group()` on `None`.** `search`, `match` and `fullmatch` return `None` when there is no match. Check `if m:` first.
3. **Validating with `search` or `match`.** They accept text that merely contains, or starts with, a valid part. Use `fullmatch`.
4. **`$` before a trailing newline.** `^\d+$` accepts `"123\n"`. Use `fullmatch` or `\A...\Z`.
5. **An unescaped dot.** `3.14` also matches `3714`. Write `\.` for a real dot, and `re.escape` for user text.
6. **`[A-z]`** includes six punctuation characters. Write `[A-Za-z]`.
7. **`\d` accepts non-ASCII digits.** Use `[0-9]` or `re.ASCII` when only 0 to 9 are allowed.
8. **Patterns that can match the empty string** (`\d*`, `(x)?`) match everywhere, and `sub` and `split` act on those empty matches. Use `+` when you mean "at least one".
9. **`findall` with groups** returns the groups, not the whole match. Use `(?:...)` for brackets that are only for structure.
10. **`|` has the lowest priority.** `^cat|dog$` is "`^cat` or `dog$`". Wrap alternatives in a group; put longer alternatives first or add `\b`.
11. **Greedy `.*`** runs to the last possible delimiter. Use a negated class like `[^"]*`, or a lazy `.*?` followed by a delimiter.
12. **Variable-width lookbehind** (`(?<=\s*)`, or alternatives of different lengths) is an error. Capture instead, or split into several lookbehinds.
13. **Flags passed by position** to `sub` or `split` land in `count`/`maxsplit`. Always write `flags=...`.
14. **Spaces and `#` in verbose patterns** are ignored. Escape them: `\ `, `\#`.
15. **Nested quantifiers over the same characters** (`(a+)+`, `(\w+\s?)+`) cause catastrophic backtracking. Make each character matchable in one way only, and test on long almost-matching input.
16. **Regex for nested or structured formats** (HTML, JSON, CSV with quotes, balanced brackets). Use a parser or a loop.
17. **Regex where a string method is enough.** `in`, `startswith`, `split`, `replace` are clearer and faster.

### 15.2 Summary

- A **regular expression** describes the **shape** of text. `re` tries the pattern at each position from the left; the **leftmost** match wins.
- **`re.search`** finds the first match anywhere, **`re.match`** only at the start, **`re.fullmatch`** the whole string (use it for **validation**). A **Match object** gives `group()`, `start()`, `end()`, `span()`, `groups()`, `groupdict()`; no match gives `None`.
- Write patterns as **raw strings**; use **`re.escape`** for text you did not write.
- **Classes** `[...]`, ranges, negation `[^...]`; shorthands `\d \w \s` and opposites `\D \W \S` (Unicode by default); the **dot** matches anything but newline.
- **Quantifiers** `* + ? {m,n}` are **greedy**; add `?` for **lazy**. Python 3.11+ adds **possessive** `*+ ++` and **atomic groups** `(?>...)`, which never give back.
- **Anchors** are zero-width: `^ $` (lines with MULTILINE), `\A \Z` (whole text), `\b \B` (word boundaries).
- **`findall`** returns strings (or group tuples), **`finditer`** Match objects, **`split`** pieces (plus separators if the pattern has a group).
- **Groups** `( )` capture and are numbered by their opening bracket; **`(?:...)`** groups without capturing; **`|`** means "or" with the lowest priority.
- **Named groups** `(?P<name>...)` and **`groupdict()`** turn text into data; **backreferences** `\1`, `(?P=name)` repeat the **same text**.
- **Lookarounds** `(?=) (?!) (?<=) (?<!)` check without consuming; lookbehind must be **fixed width**.
- **Flags**: `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`, `ASCII`, inline `(?i)`. Write long patterns in **verbose mode** with comments.
- **`re.sub`/`re.subn`** replace using `\1`, `\g<name>`, `\g<0>` or a **function** of the match. **`re.compile`** gives named, reusable patterns with their flags.
- **Catastrophic backtracking** comes from many ways to match the same characters (nested or overlapping quantifiers). Fix it by removing nesting, making separators required, using precise classes, or possessive/atomic forms; test old and new patterns on the same samples.
- **Do not use regex** for nested or structured data (HTML, JSON, CSV, brackets) or when a string method is enough.
- The **log analyser** pattern: one verbose, named-group pattern per line format, `parse_line` returning a dataclass or `None`, lazy reading with line numbers, and `Counter` summaries.

You can now extract structured fields from messy text with named groups, and explain why a pattern is slow and rewrite it. The problems in this module practise each piece in turn, from single patterns to a tokenizer, and finish with the full log analyser.

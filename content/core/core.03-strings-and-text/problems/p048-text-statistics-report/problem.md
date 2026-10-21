# Text statistics report

This is a first version of the module project: a **text statistics tool**.

Read two lines: a piece of text, and a target word. Print this report:

```
Text statistics
==========================
Characters              44
Non-space               36
Words                    9
Average length        3.89
Longest word         quick
Target word            the
Target count             2
Target share         22.2%
```

**Definitions**

- *Characters*: the length of the text line as typed.
- *Non-space*: characters that are not whitespace.
- To find the **words**: remove every character in `string.punctuation`, casefold, then `split()`.
- *Words*: how many words there are.
- *Average length*: total letters in all words divided by the number of words, 2 decimals. With no words, it is `0.00`.
- *Longest word*: the longest word; if several tie, the first one. With no words, `-`.
- *Target word*: the second input line, stripped and casefolded.
- *Target count*: how many of the words equal the target exactly.
- *Target share*: target count divided by the number of words, as a percentage with 1 decimal. With no words, `0.0%`.

**Layout**

- Line 1 is `Text statistics`, line 2 is 26 `=` signs.
- Each other line is a label left-aligned in width 16, then the value right-aligned in width 10.
- Counts use thousands separators (`1,234`).

**Tools you have not met yet**

- A list made by `split()` has a `count` method: `words.count("the")` counts items equal to `"the"`. (Lists are covered in core.05.)
- `max(words, key=len, default="-")` gives the longest word, the first one on ties, or `"-"` if there are no words.

**Example input** (gives the report above)

```
The quick brown fox jumps over the lazy dog!
THE
```

No `if` is needed: `max(len(words), 1)` avoids dividing by zero, because when there are no words the top of the fraction is 0 anyway.

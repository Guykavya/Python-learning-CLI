# Explain: it works on my laptop, but not on the server

Meena wrote this small program on her Linux laptop:

```python
with open("names.csv") as f:
    for line in f:
        print(line.strip().split(",")[0])
```

It works with her files. On the company's Windows server, three things go wrong with files from Excel:
the first name starts with a strange invisible character, a name like `Zoë` shows as `ZoÃ«` (or raises
`UnicodeDecodeError`), and when she writes a file and a colleague reads the bytes, the line ends are different
from what she expects.

In `answer.md` (about 150 to 300 words), explain:

1. What encoding `open()` uses when you do not pass `encoding=`, and why it can be different on two machines.
2. What a **BOM** is, what you see when you read such a file with `encoding="utf-8"`, and which encoding name
   removes it.
3. What **newline translation** is in text mode (read and write), and how `newline=""` or `newline="\n"` changes it.
4. A rule of three short lines she should follow in every program that touches text files.

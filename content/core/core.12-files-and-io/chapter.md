# Chapter 12: Files and I/O

So far, every program you wrote forgot everything when it ended. Your lists and dictionaries lived in memory (RAM), and RAM is wiped when the program stops. Real programs must **remember** things and **read** things that already exist: a shop keeps its prices in a file, a game keeps your high score, a script reads a log file from a server, a tool sorts the photos in a folder.

A **file** is a named piece of data on the disk. It survives after your program ends, and even after you switch the computer off. Reading and writing files is called **file I/O** (input / output). This chapter teaches you to do it **correctly**, and that means more than "it works on my laptop today". Real files can be missing, locked, huge, broken, written in another language, or cut in half by a power failure. A good program expects all of that.

By the end of this chapter you reach the three outcomes of the module:

- You can **read a multi-gigabyte file** without loading it into memory.
- You can **update a file so that a crash in the middle never corrupts it**.
- You can **build a command-line tool** with arguments, options and helpful error messages.

Along the way you will answer these questions:

- What is the difference between `"w"`, `"a"`, `"x"` and `"rb"`, and which mode can destroy your data by accident?
- What is the difference between **text** and **bytes**, and why does `open("file.txt")` work on your laptop but break on a Windows machine?
- What does `with open(...) as f` really do, and how do you write your own `with`-block tool?
- How can a program read a 20 GB file with only a few kilobytes of memory?
- Why is "erase the file, then write the new content" dangerous, and what is the safe recipe?
- How do you read and write **CSV**, **JSON**, **TOML** and **INI** files?
- Why is `pickle` dangerous?
- What are `stdin`, `stdout` and `stderr`, and how does `argparse` turn a script into a proper tool?

A note on how examples are shown. Every block of code is followed by the exact output produced by really running it with **Python 3.14** in an empty scratch folder, on Linux. Paths in tracebacks are shown as `/home/you/project`; yours will differ. Outputs that depend on your machine, such as **memory sizes** and file sizes, are labelled in the text; only the idea matters, not the number. Answer every "Predict the output" question on paper before you open the answer.

What this chapter leaves out on purpose: classes come in core.14, so you will **use** objects such as `Path`, file objects and `csv.reader` without learning how to **build** such objects. Your own modules come in core.13.

**Safety.** This chapter touches your real disk. Work inside an empty practice folder, for example `~/practice`. Be careful with anything that erases or overwrites (`"w"` mode, `os.remove`, `shutil.rmtree`). A wrong path in a delete command cannot be undone.

## Table of contents

1. [Why files matter](#1-why-files-matter)
2. [Opening a file: `open()` and modes](#2-opening-a-file-open-and-modes)
3. [Reading and writing text](#3-reading-and-writing-text)
4. [Text and bytes: encodings](#4-text-and-bytes-encodings)
5. [`with`: closing files for you](#5-with-closing-files-for-you)
6. [When things go wrong: file errors](#6-when-things-go-wrong-file-errors)
7. [Streaming big files](#7-streaming-big-files)
8. [Safe overwrites](#8-safe-overwrites)
9. [`pathlib` in depth](#9-pathlib-in-depth)
10. [`os`, `shutil` and `glob`](#10-os-shutil-and-glob)
11. [CSV files](#11-csv-files)
12. [JSON files](#12-json-files)
13. [TOML and `configparser`](#13-toml-and-configparser)
14. [`pickle` and its risks](#14-pickle-and-its-risks)
15. [`tempfile`: temporary files](#15-tempfile-temporary-files)
16. [Standard streams: stdin, stdout, stderr](#16-standard-streams-stdin-stdout-stderr)
17. [`argparse`: command-line tools](#17-argparse-command-line-tools)
18. [Project: a file organiser CLI](#18-project-a-file-organiser-cli)
19. [Common traps](#19-common-traps)
20. [Summary](#20-summary)

## 1. Why files matter

### 1.1 Memory forgets, disk remembers

Variables live in **RAM**. RAM is fast but **volatile**: when the program ends, the operating system takes the memory back. A **disk** is slower but **persistent**: the bytes stay.

| | RAM (variables) | Disk (files) |
|---|---|---|
| Speed | very fast | much slower |
| Size | small (4 to 16 GB) | large (hundreds of GB) |
| After the program ends | gone | still there |
| After a crash or power cut | gone | there, **but maybe half written** |

Look at the last row. It is the reason for half of this chapter.

### 1.2 What is a file, really?

To the operating system, a file is a **name** that points to a long row of **bytes** (numbers from 0 to 255). The name lives in a **folder** (also called a **directory**). The bytes do not say "this is text" or "this is a photo". The *meaning* comes from how a program **interprets** them. A **text file** holds bytes that spell characters (`.txt`, `.py`, `.csv`, `.json`). A **binary file** has another structure (`.jpg`, `.zip`, `.pdf`). The suffix is only a **hint**: renaming `photo.jpg` to `photo.txt` does not change one byte.

### 1.3 The life of a file operation

Almost every file program follows four steps:

1. **Open** the file. You get a **file object**, which remembers *where you are* in the file.
2. **Read or write** through that object.
3. **Close** the file, so that everything is saved and the resources are freed.
4. Handle **errors** at any step: the file may not exist, you may have no permission, the disk may be full.

### 1.4 Paths: where is the file?

You name a file with a **path**. An **absolute path** starts at the root of the disk: `/home/you/project/notes.txt` (Linux, macOS) or `C:\Users\you\project\notes.txt` (Windows). A **relative path** such as `data/prices.csv` starts at the **current working directory**, the folder your program was started from, so it can mean different files on different runs.

A very common problem is: "it works in my editor but says *file not found* in the terminal". The cause is almost always a different working directory. Section 9 shows `Path(__file__)` as the cure. Linux and macOS separate folders with `/`; Windows uses `\` (and also accepts `/`). `pathlib` hides the difference.

## 2. Opening a file: `open()` and modes

### 2.1 The first example

```python
open(file, mode="r", encoding=None, errors=None, newline=None)
```

These are the options that matter. We write a small file, then read it back.

```python
f = open("notes.txt", "w")
f.write("first line\n")
f.write("second line\n")
f.close()

f = open("notes.txt", "r")
text = f.read()
f.close()

print(repr(text))
print(type(f))
print(f.closed)
```
```text
'first line\nsecond line\n'
<class '_io.TextIOWrapper'>
True
```

- `open("notes.txt", "w")` opens (and creates) the file for **writing**. The second argument is the **mode**.
- `f.write(...)` writes text. It does **not** add a newline; we add `\n` ourselves.
- `f.close()` finishes the work. `f.read()` returns the **whole content** as one string.
- The object `f` is a `_io.TextIOWrapper`, the type of a text file object.

The weak point is the manual `f.close()`: if the code crashes before it, the file stays open. Section 5 fixes this with `with`.

### 2.2 The mode string

The **mode** says what you want to do, whether you work with text or bytes, and whether the file may be changed.

| Mode | Meaning | If the file exists | If it does not exist |
|---|---|---|---|
| `"r"` | read (the default) | opens it at the start | `FileNotFoundError` |
| `"w"` | write | **erases everything** at once | creates it |
| `"a"` | append | opens it, writes at the **end** | creates it |
| `"x"` | create, exclusive | `FileExistsError` | creates it |
| `"r+"` | read **and** write | opens it at the start | `FileNotFoundError` |

Add a letter for the kind of data: `"t"` is **text** (the default) and `"b"` is **binary** (you read and write `bytes`). So `"rb"` reads bytes, `"wb"` writes bytes, `"ab"` appends bytes.

The most important fact: **`"w"` erases the old content the moment you call `open`**, before you write anything. If the program crashes on the next line, the old data is already gone.

```python
def show(name):
    with open(name, "r") as f:
        return f.read()

with open("log.txt", "w") as f:
    f.write("one\n")
print("after first w:", repr(show("log.txt")))

with open("log.txt", "w") as f:
    f.write("two\n")
print("after second w:", repr(show("log.txt")))

with open("log.txt", "a") as f:
    f.write("three\n")
print("after a:", repr(show("log.txt")))
```
```text
after first w: 'one\n'
after second w: 'two\n'
after a: 'two\nthree\n'
```

The second `"w"` threw away `"one"`. The `"a"` mode kept `"two"` and added `"three"`. For a log file use `"a"`. To start fresh use `"w"`, but only when you are sure.

Mode `"x"` means "create, and **fail** if it exists". Use it when overwriting would be a bug (a dated report, a backup, a lock file). A second `open("once.txt", "x")` raises `FileExistsError`.

A word about `"r+"`: it opens an existing file for reading and writing, with one cursor. Python reads a whole block into a buffer, so a write after a read often lands somewhere you did not expect (at the end of the file). Avoid `"r+"` for text. Read the file, change the text in memory, and write it back safely (section 8).

## 3. Reading and writing text

### 3.1 Four ways to read

In the next examples, the file `poem.txt` holds four lines: `Roses are red`, `Violets are blue`, `Python is neat` and `And so are you`.

```python
with open("poem.txt") as f:
    print(repr(f.read(8)))
    print(repr(f.read(8)))
with open("poem.txt") as f:
    print(repr(f.readline()))
    print(repr(f.readline()))
with open("poem.txt") as f:
    print(f.readlines())
```
```text
'Roses ar'
'e red\nVi'
'Roses are red\n'
'Violets are blue\n'
['Roses are red\n', 'Violets are blue\n', 'Python is neat\n', 'And so are you\n']
```

| Call | Gives you | Use it when |
|---|---|---|
| `f.read()` | the whole rest of the file as one `str` | the file is small |
| `f.read(8)` | at most 8 **characters** | you read in blocks (section 7) |
| `f.readline()` | one line, **including** its `\n` | one line at a time |
| `f.readlines()` | a list of all lines, with `\n` | small file, and you need a list |

The file object remembers its **position**. The second `read(8)` continues where the first stopped, and two identical `readline()` calls return two different lines. An empty string `""` means **end of file**. A blank line in the file is not `""`; it is `"\n"`.

Because of the position, a file is **used up** after reading, like the generators of core.10: a second `f.read()` returns `""`.

To read again, keep the text in a variable, call `f.seek(0)` (go to the start; `f.tell()` tells the position), or open the file again.

### 3.2 The best way: loop over the file

A file object is **iterable**: a `for` loop gives one line at a time.

```python
with open("poem.txt") as f:
    for number, line in enumerate(f, start=1):
        print(number, repr(line))

print("--- stripped ---")
with open("poem.txt") as f:
    for line in f:
        print(line.rstrip("\n").upper())
```
```text
1 'Roses are red\n'
2 'Violets are blue\n'
3 'Python is neat\n'
4 'And so are you\n'
--- stripped ---
ROSES ARE RED
VIOLETS ARE BLUE
PYTHON IS NEAT
AND SO ARE YOU
```

This is the way to read text files. It reads **one line at a time**, so the file can have any size. Each `line` still ends with `"\n"`: cut it with `line.rstrip("\n")`. If you forget, `print(line)` shows a blank line between all lines, because `print` adds its own newline. `enumerate(f, start=1)` gives line numbers for messages like "line 17: bad value".

### 3.3 Predict the output

**Predict the output.** Write down all the printed lines before you open the answer.

```python
with open("n.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("n.txt") as f:
    print(f.read(3))
    print(f.readline())
    print(f.readline().strip())
    rest = f.read()
    print(len(rest))
    print(f.readline() == "")
```
<details><summary>Answer</summary>

```text
alp
ha

beta
6
True
```


`read(3)` takes `alp`. Then `readline()` continues from the cursor and returns the **rest of the current line**, `ha\n`; `print` adds a second newline, so a blank line follows. The next `readline()` gives `beta\n` (we `strip` it). What is left is `gamma\n`, 6 characters. At the end of the file `readline()` returns `""`.
</details>

### 3.4 Writing

`f.write(text)` writes a **string** and returns the number of characters. It never adds a newline. Three common ways to write many lines:

```python
lines = ["apple", "banana", "cherry"]

with open("fruits.txt", "w") as f:
    for name in lines:
        f.write(name + "\n")

with open("fruits.txt", "w") as f:
    pass

with open("fruits2.txt", "w") as f:
    f.writelines(name + "\n" for name in lines)
    print("n =", f.write("tail"))

with open("fruits2.txt") as f:
    print(repr(f.read()))
```
```text
n = 4
'apple\nbanana\ncherry\ntail'
```

- A `for` loop with `f.write(name + "\n")` is the clearest.
- `f.writelines(iterable)` writes every string of the iterable. Despite the name, it **adds no newlines**.
- Opening with `"w"` and writing nothing leaves an **empty** file: the `pass` block above emptied `fruits.txt`.

`print()` can write to a file too and takes care of the newline, `sep` and `end`: `print("items:", 3, file=f)`.

`write` accepts **strings only**: `f.write(42)` raises `TypeError`. Use `str(42)` or an f-string such as `f"{3.14159:.2f}"`.

### 3.5 Buffering: when do the bytes reach the disk?

Writing to a disk is slow, so Python collects what you write in a **buffer** and hands it to the operating system in bigger pieces. The data is only guaranteed to be handed over when you **close** or **flush** the file.

```python
import os
f = open("buf.txt", "w")
f.write("hello")
print("size on disk before flush:", os.path.getsize("buf.txt"))
f.flush()
print("size on disk after flush: ", os.path.getsize("buf.txt"))
f.close()
```
```text
size on disk before flush: 0
size on disk after flush:  5
```

Before `flush()` the file on disk had **0 bytes**, although we had written 5 characters. `close()` and the end of a `with` block flush too, so normally you do not notice. You notice when a program crashes and the last lines are missing from a log, or when another program reads the file while yours is still writing. Use `f.flush()` or `print(..., flush=True)`. (Even `flush()` only hands the data to the operating system; `os.fsync` pushes it to the physical disk, see section 8.)

### 3.6 Predict the output

**Predict the output.** Remember what `"w"` does at the moment of `open`.

```python
with open("a.txt", "w") as f:
    f.write("one")
with open("a.txt", "a") as f:
    f.write("two\n")
with open("a.txt", "w") as f:
    f.write("three\n")
with open("a.txt", "a") as f:
    f.write("four")
    f.write("five\n")
with open("a.txt") as f:
    print(f.read().split())
```
<details><summary>Answer</summary>

```text
['three', 'fourfive']
```


After the first block the file is `one`; the `"a"` block makes it `onetwo\n`. Then `"w"` erases everything and writes `three\n`. The last `"a"` block adds `four` and `five\n` **without a newline in between**, so the file holds `three\nfourfive\n`. `split()` gives two words. `write` never adds a space or a newline for you.
</details>


## 4. Text and bytes: encodings

This section explains most "weird characters" problems. Read it slowly.

### 4.1 Characters are not bytes

A Python `str` is a sequence of **characters**: letters, digits, `₹`, `é`, emoji. A disk can only hold **bytes**. To store a string, Python converts it to bytes. That conversion is **encoding**; the reverse is **decoding**. The rule that maps characters to bytes has a name, such as `utf-8`.

```python
text = "naïve café"
print(len(text), "characters")
data = text.encode("utf-8")
print(len(data), "bytes")
print(data)
print(list(data[:6]))
print(data.decode("utf-8"))
print(type(text), type(data))
```
```text
10 characters
12 bytes
b'na\xc3\xafve caf\xc3\xa9'
[110, 97, 195, 175, 118, 101]
naïve café
<class 'str'> <class 'bytes'>
```

`"naïve café"` has **10 characters** but **12 bytes**: `ï` and `é` need two bytes each in UTF-8. A `bytes` object prints as `b'...'`; indexing it gives **integers** (0 to 255), not one-letter strings. `str` and `bytes` are different types, and Python never mixes them silently.

### 4.2 UTF-8, the encoding to use

**Unicode** gives every character in the world a number. **UTF-8** is the most common way to turn those numbers into bytes, and it has variable length: `"A"` takes 1 byte, `"é"` 2, `"₹"` 3 and `"😀"` 4.

ASCII characters (A to Z, digits, simple punctuation) take **1** byte, so old English-only files are valid UTF-8. Other encodings (`utf-16`, `latin-1`, `cp1252`) are **not** compatible with UTF-8.

**Rule: always read and write text with `encoding="utf-8"`.** Be explicit; do not trust the default.

### 4.3 What happens with the wrong encoding

If you read a file with another encoding than the one it was written with, you get **garbage characters** (*mojibake*) or an **error**.

```python
with open("u8.txt", "w", encoding="utf-8") as f:
    f.write("café ₹")

with open("u8.txt", encoding="latin-1") as f:
    print("as latin-1:", f.read())

try:
    with open("u8.txt", encoding="ascii") as f:
        f.read()
except UnicodeDecodeError as e:
    print("as ascii:", e)
```
```text
as latin-1: cafÃ© â¹
as ascii: 'ascii' codec can't decode byte 0xc3 in position 3: ordinal not in range(128)
```

`latin-1` can decode **any** byte, so it never fails, but it turns `é` into `Ã©`. That is the typical sign of "UTF-8 read as Latin-1". `ascii` refuses bytes above 127 with `UnicodeDecodeError`, and the message names the codec, the byte and the position. Writing can fail too: `open("a.txt", "w", encoding="ascii").write("₹")` raises `UnicodeEncodeError`. Both errors are subclasses of `ValueError`, **not** of `OSError`.

### 4.4 The `errors=` option

By default (`errors="strict"`) a problem raises an exception. You can choose another policy:

```python
with open("bad.txt", "wb") as f:
    f.write(b"caf\xe9 ok")      # latin-1 byte for e-acute: not valid utf-8

for mode in ["strict", "replace", "ignore", "backslashreplace"]:
    try:
        with open("bad.txt", encoding="utf-8", errors=mode) as f:
            print(mode, "->", repr(f.read()))
    except UnicodeDecodeError as e:
        print(mode, "-> UnicodeDecodeError")

with open("out.txt", "w", encoding="ascii", errors="replace") as f:
    f.write("50 ₹")
print(open("out.txt").read())
```
```text
strict -> UnicodeDecodeError
replace -> 'caf� ok'
ignore -> 'caf ok'
backslashreplace -> 'caf\\xe9 ok'
50 ?
```

| `errors=` | Effect | When to use |
|---|---|---|
| `"strict"` | raises an error (default) | you want to **know** about broken data |
| `"replace"` | bad bytes become `�` (or `?` when writing) | display, counting |
| `"ignore"` | bad bytes disappear silently | rarely good: data is lost without a trace |
| `"backslashreplace"` | bad bytes shown as `\xe9` | logs and debugging: you keep the evidence |

For unknown files from outside (uploads, logs), read with `errors="replace"` so that one bad byte does not kill the program. Keep `"strict"` for your own data.

### 4.5 The default-encoding trap

Without `encoding`, Python picks a default that depends on the computer (`locale.getpreferredencoding(False)` shows it).

On this Linux machine it is UTF-8. On many Windows machines it is a legacy encoding such as `cp1252`. The same program then writes different bytes, and a file made on one computer shows garbage on the other. So write `open(path, encoding="utf-8")` every time. It is a few extra characters, and it removes a whole class of bugs.

### 4.6 The BOM: an invisible character

Some Windows programs (Notepad, Excel) write a **byte order mark** (BOM) at the start of a UTF-8 file: the bytes `EF BB BF`. Read with plain `utf-8`, it shows up as an invisible `\ufeff` glued to your first value, so `"name" == "\ufeffname"` is false. The encoding `utf-8-sig` removes it (`open(path, encoding="utf-8-sig")`).

If a CSV from Excel has a first column that "does not exist" although you see it in the header, suspect a BOM.

### 4.7 Binary mode: `"rb"` and `"wb"`

For images, ZIP files and anything that is not text, use binary mode. You read and write `bytes`, with **no encoding and no newline translation**.

```python
with open("pic.bin", "wb") as f:
    f.write(bytes([137, 80, 78, 71, 0, 255]))
    f.write(b"PNG")

with open("pic.bin", "rb") as f:
    data = f.read()
print(data)
print(len(data), data[0], data[1:4])
print(type(data), type(data[0]))

try:
    with open("pic.bin", "r") as f:
        f.read()
except UnicodeDecodeError as e:
    print("UnicodeDecodeError:", e)
```
```text
b'\x89PNG\x00\xffPNG'
9 137 b'PNG'
<class 'bytes'> <class 'int'>
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x89 in position 0: invalid start byte
```

Reading these bytes as text fails at the first byte (`0x89`), which is not valid UTF-8. Rule of thumb: `UnicodeDecodeError` means the file is **not text**, or has **another encoding**. The opposite mistake also fails: `f.write("hello")` on a binary file raises `TypeError`. Convert with `text.encode("utf-8")` before writing and `data.decode("utf-8")` after reading.

### 4.8 Newlines: `\n`, `\r\n` and `newline=`

Linux and macOS end a line with `\n`; Windows uses `\r\n`. In **text mode** Python hides this: on reading, `\r\n` becomes `\n`; on writing, `\n` becomes the platform's line ending. The `newline=` parameter controls it.

```python
with open("crlf.txt", "wb") as f:
    f.write(b"one\r\ntwo\r\nthree\r\n")

with open("crlf.txt", "r") as f:
    print("default      :", repr(f.read()))
with open("crlf.txt", "r", newline="") as f:
    print("newline=''   :", repr(f.read()))
with open("crlf.txt", "r", newline="\n") as f:
    print("newline='\\n' :", repr(f.read()))
```
```text
default      : 'one\ntwo\nthree\n'
newline=''   : 'one\r\ntwo\r\nthree\r\n'
newline='\n' : 'one\r\ntwo\r\nthree\r\n'
```

- `newline=None` (default): translate on reading and writing, as described.
- `newline=""` when reading: **no translation**, you see the original `\r\n`. Lines are still split correctly.
- `newline="\n"` when writing means "write `\n` exactly"; `newline="\r\n"` writes Windows endings on any system.

You need `newline=""` in one very important place: the **csv** module (section 11). Remember the spelling now.

### 4.9 Predict the output

**Predict the output.** Think about how many bytes each character needs.

```python
for text in ["abc", "café", "₹100", "😀"]:
    print(len(text), len(text.encode("utf-8")))
data = "é".encode("utf-8")
print(data, data[0], len(data))
print(b"abc"[0], b"abc"[:1])
```
<details><summary>Answer</summary>

```text
3 3
4 5
4 6
1 4
b'\xc3\xa9' 195 2
97 b'a'
```


ASCII is 1 byte per character, so `abc` is 3 and 3. `café` has the 2-byte `é`: 4 characters, 5 bytes. `₹100` is the 3-byte rupee sign plus three digits: 4 and 6. The emoji is 1 character and 4 bytes. `"é".encode()` is `b'\xc3\xa9'`; indexing gives the integer 195. `b"abc"[0]` is an **integer** (97) but the **slice** `b"abc"[:1]` is bytes again (`b'a'`).
</details>

## 5. `with`: closing files for you

### 5.1 Why closing matters

Every open file uses a resource of the operating system, which allows only a limited number per program. More important, **buffered data is saved only when the file is closed or flushed**.

```python
f = open("lost.txt", "w")
f.write("data we hoped to save")
# no f.close() here ...
import os
print("on disk now:", os.path.getsize("lost.txt"), "bytes")
f.close()
print("after close:", os.path.getsize("lost.txt"), "bytes")
```
```text
on disk now: 0 bytes
after close: 21 bytes
```

We had written 21 characters, but the file on disk had **0 bytes** until `close()`. A crash in between loses the data. (CPython also closes a file when its object is deleted, but never rely on that.) You could write `try: ... finally: f.close()` each time. Python has a shorter tool.

### 5.2 `with open(...) as f`

The `with` statement runs a block and **guarantees** a cleanup step when the block ends, however it ends: normally, with `return`, with `break`, or with an exception.

```python
f = open("notes.txt", "w")
f.write("data")
f.close()

with open("notes.txt") as f:
    print(f.closed)
    data = f.read()
print(f.closed)
print(data)

try:
    f.read()
except ValueError as e:
    print("ValueError:", e)
```
```text
False
True
data
ValueError: I/O operation on closed file.
```

Inside the block `f.closed` is `False`; after it, `True`, and using `f` raises `ValueError: I/O operation on closed file.` The name `f` still exists after the block, but the file behind it is closed. Read the data **inside** the block and keep it in a variable.

`with` also works when something goes wrong:

```python
try:
    with open("w.txt", "w") as f:
        f.write("saved before the crash\n")
        raise RuntimeError("something broke")
except RuntimeError as e:
    print("caught:", e, f.closed)       # caught: something broke True
```

The error was raised inside the block, and still the file was closed and the written line was saved. The exception was not hidden: it went upward and we caught it outside. You can open several files in one `with`, separated by commas: `with open(a) as src, open(b, "w") as dst:`. They are closed in reverse order.

### 5.3 What `with` really does

`with X as name:` means: call the **enter** step of `X` and bind the result to `name`; run the block; call the **exit** step, even if the block raised. Objects that support this are **context managers**. File objects are context managers whose exit step is `close()`. So are locks, database connections, temporary folders (section 15) and `redirect_stdout` (section 16).

You can watch the steps with a small object. It uses a **class**, which comes in core.14, so this is only a **peek, comes in core.14**: ignore the syntax and watch the order of the printed lines.

```python
class Shout:
    def __enter__(self):
        print("entering")
        return "value"
    def __exit__(self, exc_type, exc, tb):
        print("leaving, error was:", exc_type)
        return False

with Shout() as v:
    print("inside with", v)
```
```text
entering
inside with value
leaving, error was: None
```

`__enter__` ran first and its return value became `v`; then the block; then `__exit__` ran and received `None` (no error).

### 5.4 Your own context manager with `@contextmanager`

You do not need a class. The decorator `contextlib.contextmanager` (core.11) turns a **generator function** (core.10) with one `yield` into a context manager. The code **before** `yield` is the *enter* step, the yielded value is what `as name` receives, and the code **after** `yield` is the *exit* step.

```python
from contextlib import contextmanager

@contextmanager
def announce(name):
    print("start", name)
    try:
        yield name.upper()
    finally:
        print("stop ", name)

with announce("job") as value:
    print("inside, got", value)
try:
    with announce("bad job"):
        1 / 0
except ZeroDivisionError:
    print("error passed through")
```
```text
start job
inside, got JOB
stop  job
start bad job
stop  bad job
error passed through
```

If the block raises, Python throws the exception into the generator **at the `yield` line**. Without `try/finally` the cleanup would be skipped. The second run shows `stop  bad job` printed and the `ZeroDivisionError` still coming out: cleanup runs, and the error is not swallowed.

**Rule: always put `yield` inside `try:` and the cleanup in `finally:`.** Two ideas for your own tools: a **timer** (`start = time.perf_counter()` before the `yield`, print the elapsed time in `finally`) and a **working-directory changer** (`os.chdir(folder)` before, `os.chdir(old)` in `finally`). In section 8 you will build a safe `atomic_open` the same way.

### 5.5 `contextlib.suppress`

"Do this, and if the file is already gone, never mind" is common. Instead of `try/except/pass` you can write `with suppress(FileNotFoundError): os.remove("junk.txt")` (after `from contextlib import suppress`). It ignores that error type **inside the block** only. Use it when ignoring is the true intention; never `suppress(Exception)`.

### 5.6 Predict the output

**Predict the output.** Is the file closed when the `KeyError` is caught?

```python
def read_first(path):
    with open(path) as f:
        return f.readline()

with open("t.txt", "w") as f:
    f.write("first\nsecond\n")
print(repr(read_first("t.txt")))
try:
    with open("t.txt") as f:
        for line in f:
            print(line.strip())
            raise KeyError("stop")
except KeyError:
    print("closed?", f.closed)
```
<details><summary>Answer</summary>

```text
'first\n'
first
closed? True
```


`read_first` returns from **inside** the `with`. The `return` does not skip the cleanup: the file is closed on the way out and the function gives back `'first\n'`. In the second part the `KeyError` is raised in the middle of the loop; `with` closes the file while the error travels up, so `f.closed` is `True` in the `except` block.
</details>

## 6. When things go wrong: file errors

Files live in the outside world, and the outside world fails. Expect it.

### 6.1 The family of OS errors

Errors from the operating system are subclasses of **`OSError`**, and common ones have their own names.

| Exception | What happened | Typical cause |
|---|---|---|
| `FileNotFoundError` | file or folder does not exist | typo, wrong working directory |
| `PermissionError` | you may not do this | read-only file, system folder |
| `IsADirectoryError` | you opened a folder like a file | missing file name in the path |
| `NotADirectoryError` | a part of the path is a file | `notes.txt/data.txt` |
| `FileExistsError` | it exists already | mode `"x"`, `mkdir`, `copytree` |
| `OSError` (parent of all) | any other OS problem | disk full, device error |

`IOError` is an old name for `OSError` (`IOError is OSError` is `True`), so you may meet it in old code. An OS error carries `errno` (a number), `strerror` (text for people) and `filename`.

```python
try:
    open("missing_folder/file.txt", "w")
except FileNotFoundError as e:
    print("FileNotFoundError:", e)
```
```text
FileNotFoundError: [Errno 2] No such file or directory: 'missing_folder/file.txt'
```

Look at the case above: opening `missing_folder/file.txt` for **writing** fails because the **folder** does not exist. Mode `"w"` creates a missing file, never a missing folder. Create the folder first (`Path.mkdir(parents=True, exist_ok=True)`, section 9). `PermissionError` appears the same way, for example when you open a read-only file for writing (on Linux as the root user permission checks are skipped, so you may not see it there).

### 6.2 `errno`: telling errors apart

Sometimes you catch the general `OSError` and look at the number, because no special class exists. The module `errno` has readable names (`errno.ENOENT` is 2, `EACCES` 13, `EEXIST` 17, `ENOSPC` 28).

For example, to handle a full disk, catch `OSError` and test `e.errno == errno.ENOSPC`. The numbers differ between operating systems, so use the names.

### 6.3 Which errors to catch?

Catch the **specific** errors you know how to handle and let all others rise.

```python
def read_config(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"{path}: file not found, using defaults")
        return ""
    except OSError as e:
        print(f"{path}: other OS problem: {e}")
        raise

print(repr(read_config("settings.txt")))
```
```text
settings.txt: file not found, using defaults
''
```

`FileNotFoundError` is handled: we use defaults. Other `OSError`s are re-raised with a bare `raise`, because we do not know how to fix them. **Order matters**: specific classes first, `OSError` last, because `FileNotFoundError` is also an `OSError`. If `OSError` came first, the later `except` lines would never run.

### 6.4 "Look before you leap" or "ask forgiveness"?

To handle a file that might not exist, you can check first (**LBYL**: `if os.path.exists(path): ...`) or just try and catch the error (**EAFP**: `try: open(...) except FileNotFoundError: ...`). Prefer **EAFP** for files. Between your check and your `open`, another program can delete or create the file, so the check can be true and the `open` still fail (a **race condition**). Also, `exists` says nothing about permissions. With `try/except` there is no gap.

### 6.5 Decode errors are not OS errors

`UnicodeDecodeError` is a `UnicodeError`, which is a `ValueError`. So `except OSError:` does **not** catch it. If you read files of unknown encoding, catch both: `except (OSError, UnicodeDecodeError)`.

### 6.6 Messages for people

When a command-line tool fails, show a short human message, not a traceback. Use `e.strerror`, name the file, and write to **stderr** (section 16): `print(f"error: cannot read {path!r}: {e.strerror}", file=sys.stderr)`. Section 17 turns this into an **exit code**.


## 7. Streaming big files

### 7.1 The problem: the file is bigger than the memory

Imagine a server log of 20 GB and a laptop with 8 GB of RAM. The code `text = f.read()` tries to put all 20 GB into memory. The operating system will kill your program, or freeze your whole session, long before it finishes. Even a 2 GB file can freeze a small laptop, because a Python string needs memory for the whole text, and `readlines()` needs even more: one string object for each line.

The solution is **streaming**: read a **small piece**, handle it, forget it, read the next piece. At any moment only one piece is in memory, so the memory use is **constant**, for a thousand lines or a billion. This is the idea of the generators in core.10: produce values one at a time, on demand. A file object is already such a stream. There are two kinds of pieces: **lines** (text files whose lines are not huge) and **chunks** of a fixed number of bytes (binary files, or text without useful lines).

### 7.2 A test file (without the 20 GB)

You do not need a giant file to learn the idea, and a giant file on a small laptop is dangerous. We create a log file of 100,000 lines (about 5 MB), written **line by line**, so even the writer never holds the whole content.

```python
import os, random

def make_log(path, n_lines):
    """Write n_lines fake log lines, one at a time (never holds them all)."""
    random.seed(1)
    levels = ["INFO", "INFO", "INFO", "WARN", "ERROR"]
    with open(path, "w", encoding="utf-8") as f:
        for i in range(n_lines):
            level = random.choice(levels)
            f.write(f"2026-01-01 10:{i % 60:02d}:00 {level} request {i} took {random.randint(1, 900)} ms\n")

make_log("big.log", 100_000)
print(os.path.getsize("big.log") // 1024, "KB")
with open("big.log") as f:
    for _ in range(3):
        print(f.readline(), end="")
```
```text
4977 KB
2026-01-01 10:00:00 INFO request 0 took 583 ms
2026-01-01 10:01:00 INFO request 1 took 262 ms
2026-01-01 10:02:00 INFO request 2 took 508 ms
```

The `for` loop produces one line at a time and writes it: `make_log` is itself a streaming program. (The sizes shown are for this run.)

### 7.3 Line by line: constant memory

We count the `ERROR` lines in three ways and measure the **peak memory** with `tracemalloc`. `tracemalloc` is a standard tool that measures the memory used by Python objects (core.20 teaches it; here you only read its numbers). The numbers are machine-specific; the comparison is what matters.

```python
import tracemalloc

def count_all_at_once(path):
    with open(path) as f:
        text = f.read()
    return text.count("ERROR")

def count_with_readlines(path):
    with open(path) as f:
        lines = f.readlines()
    return sum(1 for line in lines if "ERROR" in line)

def count_streaming(path):
    n = 0
    with open(path) as f:
        for line in f:
            if "ERROR" in line:
                n += 1
    return n

for func in [count_all_at_once, count_with_readlines, count_streaming]:
    tracemalloc.start()
    result = func("big.log")
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{func.__name__:22} errors={result}  peak memory={peak / 1024:9.1f} KB")
```
```text
count_all_at_once      errors=20149  peak memory=  10084.5 KB
count_with_readlines   errors=20149  peak memory=   9901.2 KB
count_streaming        errors=20149  peak memory=    145.4 KB
```

- `count_all_at_once` reads the **whole text**: its peak is about the size of the file (Python text needs a bit more than the bytes on disk).
- `count_with_readlines` builds a **list of all lines**: about the same.
- `count_streaming` iterates the file: the peak is about **145 KB**, mostly the internal buffer, and **that number would stay the same for a 20 GB file**.

All three give the same answer; only the memory differs. For a file 4,000 times bigger, the first two would need about 40 GB. The third still needs about 145 KB. **That is the first outcome of this module: you can read a multi-gigabyte file without loading it into memory.** The price is time: the whole file still passes through the disk, so 20 GB takes minutes. But it **works**.

The streaming rules:

1. Use `for line in f:`. Never `f.read()` or `f.readlines()` for files that may be big.
2. Do not store the lines. Keep **summaries**: counters, totals, the best few items.
3. If you must keep something per line (the set of all user names), ask how big *that* will be.
4. Writing is a stream too: write each result when you have it, not after collecting a billion results in a list.

### 7.4 Keeping only the end

To get the **last few lines** of a huge file (like the `tail` command), keep a small list and drop the oldest line when it grows. (In core.17 you will meet `collections.deque(f, maxlen=3)`, which does exactly this for you.) The idea is always the same: memory stays small, because you keep only what you need.

### 7.5 A generator pipeline over a file

In core.10 you chained generators into **pipelines**. A file is the perfect source.

```python
def read_lines(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")

def only_level(lines, level):
    for line in lines:
        if f" {level} " in line:
            yield line

def milliseconds(lines):
    for line in lines:
        yield int(line.split()[-2])

times = milliseconds(only_level(read_lines("big.log"), "ERROR"))

count = total = 0
for ms in times:
    count += 1
    total += ms
print("ERROR lines:", count)
print("average ms :", round(total / count, 1))
```
```text
ERROR lines: 20149
average ms : 450.6
```

`read_lines` yields one clean line at a time (the `with` inside the generator keeps the file open while the generator lives, and closes it at the end). `only_level` keeps the ERROR lines. `milliseconds` extracts a number. The final `for` loop pulls values through all three stages, one at a time, so **no stage ever holds more than one line**. A 5 MB file became three numbers, and the same code works for 50 GB. A lazy pipeline can also stop early: with `itertools.islice(errors, 3)` only the first three matches are read and the rest of the file is **never touched**.

### 7.6 Chunks: when there are no lines

A binary file (video, ZIP, disk image) has no lines, and a text file can be one monstrous line. Iterating "by line" then gives one huge piece and no saving at all. Read **fixed-size chunks** instead.

The usual idiom uses `iter(callable, sentinel)`. With two arguments, `iter` takes a function with no arguments and a **sentinel** value: it calls the function again and again, and stops when the function returns the sentinel.

```python
data = [3, 5, 0, 7, 9]
pos = 0
def next_value():
    global pos
    value = data[pos]
    pos += 1
    return value

print(list(iter(next_value, 0)))
```
```text
[3, 5]
```

The values come from calls to `next_value()`: 3, 5, then `0`, the sentinel, which ends the loop (the sentinel itself is not given out). For a file, the function is `lambda: f.read(size)` and the sentinel is what `read` returns at the end: `b""` in binary mode, `""` in text mode.

With a file, the loop looks like `for chunk in iter(lambda: f.read(64 * 1024), b""):`. `f.read(65536)` returns at most that many bytes, and fewer at the end. The `lambda` is a closure over `f`, so each call continues where the last stopped. Typical chunk sizes are 8 KB to 1 MB; the exact value is not critical. Two real jobs for chunks are copying a file and hashing it. `hashlib.sha256().update(chunk)` accepts the data piece by piece, so the fingerprint of a 50 GB file needs a few kilobytes of memory. Two files with the same hash have the same content, which is how duplicate finders and download checkers work. (In text mode, `read(n)` reads *n characters*, not bytes.)

### 7.7 Predict the output

**Predict the output.** `iter(f.readline, "")` is the chunk idea with lines. Where does each loop stop?

```python
import io
f = io.StringIO("ab\ncd\n\nef\n")
lines = []
for line in iter(f.readline, ""):
    lines.append(line)
print(len(lines), lines)
f.seek(0)
print([line.strip() for line in iter(f.readline, "\n")])
```
<details><summary>Answer</summary>

```text
4 ['ab\n', 'cd\n', '\n', 'ef\n']
['ab', 'cd']
```


The first loop stops only at `""`, the real end of the file. The blank line in the middle is `"\n"`, not `""`, so it is **kept**: four lines. The second loop uses `"\n"` as its sentinel, so it stops at the first blank line: `['ab', 'cd']`. A sentinel must be a value that your data cannot contain by accident.
</details>

## 8. Safe overwrites

### 8.1 The danger

You have a file `report.txt` with important data, and your program must replace it with a new version. The obvious code is:

```python
def save_report(path, lines, crash_at=None):
    with open(path, "w") as f:              # the old content is erased HERE
        for i, line in enumerate(lines):
            if i == crash_at:
                raise RuntimeError("power cut!")
            f.write(line + "\n")

save_report("report.txt", ["old 1", "old 2", "old 3"])
print("before:", open("report.txt").read().split())

try:
    save_report("report.txt", ["new 1", "new 2", "new 3", "new 4"], crash_at=2)
except RuntimeError as e:
    print("crashed:", e)

print("after :", open("report.txt").read().split())
```
```text
before: ['old', '1', 'old', '2', 'old', '3']
crashed: power cut!
after : ['new', '1', 'new', '2']
```

The program crashed after two new lines. The result is a **mixed, truncated file**: the old report is gone and the new one is incomplete. A power cut, `Ctrl+C`, a full disk, or an exception in your own code does exactly this, because `"w"` erases the old content **at the moment of `open`**. Any program that keeps data in a file (settings, a to-do list, a game save) must avoid it. A user who loses data once will not trust your program again.

### 8.2 The safe recipe

1. Write the new content to a **temporary file next to the real one** (same folder).
2. Make sure it is complete and on the disk (`flush`, then `os.fsync`).
3. **Replace** the old file with the new one in a single step: `os.replace(tmp, real)`.

At every moment, the real name points to a **complete** file: first the old one, then the new one. There is no moment when it points to something half-written.

```python
import os

def save_report(path, lines, crash_at=None):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        for i, line in enumerate(lines):
            if i == crash_at:
                raise RuntimeError("power cut!")
            f.write(line + "\n")
    os.replace(tmp_path, path)              # one atomic step

save_report("report.txt", ["old 1", "old 2", "old 3"])
try:
    save_report("report.txt", ["new 1", "new 2", "new 3", "new 4"], crash_at=2)
except RuntimeError as e:
    print("crashed:", e)
print("after crash :", open("report.txt").read().split())
print("leftover    :", sorted(n for n in os.listdir(".") if not n.endswith(".py")))

save_report("report.txt", ["new 1", "new 2", "new 3", "new 4"])
print("after success:", open("report.txt").read().split())
```
```text
crashed: power cut!
after crash : ['old', '1', 'old', '2', 'old', '3']
leftover    : ['report.txt', 'report.txt.tmp']
after success: ['new', '1', 'new', '2', 'new', '3', 'new', '4']
```

After the crash, `report.txt` still holds the complete **old** report. Study the middle line: a **leftover** `report.txt.tmp` is still there. The original is safe, but we left rubbish behind. The next version cleans up.

### 8.3 What "atomic" means

An operation is **atomic** if it happens completely or not at all, and no other program can see a half-way state. `os.replace(src, dst)` is atomic on one file system: the name `dst` switches from the old file to the new file in one step, even if the power fails at that moment. After a restart you see either the old file or the new one, never a mix. Three details:

- The temporary file must be on the **same file system**, best in the same folder. Replacing across disks is a copy, and a copy is not atomic. That is why the temp file lives next to the real one, not in `/tmp`.
- `os.replace` overwrites an existing target on all systems. Its cousin `os.rename` fails on Windows if the target exists.
- `f.flush()` empties Python's buffer into the operating system; `os.fsync(f.fileno())` asks the OS to write its own cache to the physical disk. Without `fsync`, a power cut right after the replace can still leave an empty new file on some systems.

### 8.4 A reusable tool

With `@contextmanager`, we can make the safe write look like a normal `open`. The block writes into a temporary file made by `tempfile.mkstemp` (section 15) in the same folder, and **only a successful block** triggers the replace.

```python
import os, tempfile
from contextlib import contextmanager

@contextmanager
def atomic_open(path, mode="w", **kwargs):
    folder = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=folder, suffix=".tmp")
    f = os.fdopen(fd, mode, **kwargs)
    try:
        yield f
        f.flush()
        os.fsync(f.fileno())
        f.close()
        os.replace(tmp_path, path)
    except BaseException:
        f.close()
        os.unlink(tmp_path)
        raise

with atomic_open("data.txt", encoding="utf-8") as f:
    f.write("version 1\n")
print(open("data.txt").read(), end="")

try:
    with atomic_open("data.txt", encoding="utf-8") as f:
        f.write("version 2, half written")
        raise ValueError("bug in my code")
except ValueError:
    pass
print(open("data.txt").read(), end="")
print(sorted(n for n in os.listdir(".") if not n.endswith(".py")))
```
```text
version 1
version 1
['data.txt']
```

The second block raised `ValueError` after writing half of "version 2". The file still says `version 1`, and the temporary file was removed (the listing shows only the real file). `except BaseException` also covers `KeyboardInterrupt`, so `Ctrl+C` is safe too, and the bare `raise` passes the original error on. You can use `atomic_open` instead of `open` whenever you write a whole file. **That is the second outcome of this module: a crash midway never corrupts the file.**

### 8.5 Other safe habits

- **Append-only logs** need no tricks: `"a"` only adds at the end. A crash may cut the last line but older lines stay safe.
- **Backups**: before a risky change, `shutil.copy2(path, path + ".bak")`.
- **`"x"` mode** prevents accidental overwrites of new files.
- For many records with many small updates, use a real database (SQLite). It does the temp-file work, and more, for you.

### 8.6 Predict the output

**Predict the output.** Two updates: one fails and one succeeds. What do the two result lines show?

```python
import os
with open("keep.txt", "w") as f:
    f.write("old")

def update(text, fail):
    with open("keep.txt.tmp", "w") as f:
        f.write(text)
        if fail:
            raise OSError("disk full")
    os.replace("keep.txt.tmp", "keep.txt")

for text, fail in [("new1", True), ("new2", False)]:
    try:
        update(text, fail)
    except OSError as e:
        print("failed:", e)
    print(open("keep.txt").read(), sorted(n for n in os.listdir(".") if n.startswith("keep")))
```
<details><summary>Answer</summary>

```text
failed: disk full
old ['keep.txt', 'keep.txt.tmp']
new2 ['keep.txt']
```


Case one: the exception is raised **inside** the `with` block, so `os.replace` is never reached. `keep.txt` is unchanged (`old`), but the half-finished `keep.txt.tmp` stays, because this simple version does not clean up. Case two: the block finishes, `os.replace` moves the temp file over the real file, and the `.tmp` name disappears (it was renamed). `atomic_open` also removes the temp file after a failure.
</details>

## 9. `pathlib` in depth

### 9.1 Why paths deserve their own tool

Until now we used strings as paths. That works until you must join folders, find the extension, handle `\` and `/`, or list files. People wrote `path + "/" + name` or `os.path.join(...)`. The module `pathlib` offers one clear object, a `Path`, with methods for everything. It is the modern way. A `Path` is an object (classes come in core.14; treat it as a string with superpowers) and it is **immutable**: methods return new `Path` objects.

### 9.2 Building and taking apart paths

The `/` operator joins parts, on any operating system. Attributes cut a path into pieces.

```python
from pathlib import Path

p = Path("projects") / "demo" / "report.final.txt"
print(p)
print(type(p).__name__)
print(p.name)
print(p.stem)
print(p.suffix)
print(p.suffixes)
print(p.parent)
print(p.parts)
print(p.parent.parent)
```
```text
projects/demo/report.final.txt
PosixPath
report.final.txt
report.final
.txt
['.final', '.txt']
projects/demo
('projects', 'demo', 'report.final.txt')
projects
```

`name` is the last part; `stem` is the name without the **last** suffix; `suffix` is the last suffix with its dot; `suffixes` lists all; `parent` is the folder; `parts` is a tuple of all pieces. `type(p).__name__` is `PosixPath` on Linux and macOS, and `WindowsPath` on Windows: `Path(...)` picks the right one.

### 9.3 Changing pieces

A `Path` is immutable, so these methods give a **new** path.

```python
from pathlib import Path

p = Path("photos/holiday.JPG")
print(p.with_suffix(".png"))
print(p.with_name("beach.jpg"))
print(p.with_stem("sunset"))
print(p.suffix.lower() == ".jpg")
print(Path("archive.tar.gz").suffixes, Path(".bashrc").suffix == "")
print(list(Path("a/b/c.txt").parents))
```
```text
photos/holiday.png
photos/beach.jpg
photos/sunset.JPG
True
['.tar', '.gz'] True
[PosixPath('a/b'), PosixPath('a'), PosixPath('.')]
```

- `with_suffix(".png")`, `with_name(...)` and `with_stem(...)` replace the extension, the file name, or only the stem.
- `.suffix` keeps the **original case** (`.JPG`). Compare with `p.suffix.lower() == ".jpg"`. Forgetting this is a very common bug.
- For `archive.tar.gz`, `.suffix` is `.gz`; use `.suffixes` for the full list.
- A file that only starts with a dot (`.bashrc`) has **no** suffix.
- `p.parents` lists all the ancestors, nearest first.

`PureWindowsPath(r"C:\Users\Kavya\notes.txt")` and `PurePosixPath` parse paths of the other system without touching the disk. They are useful for tests.

### 9.4 Absolute, relative, `resolve`

```python
from pathlib import Path

p = Path("sub/file.txt")
print(p.is_absolute())
print(p.resolve().is_absolute())
print(p.resolve().relative_to(Path.cwd()))
print(Path("/a/b/c.txt").relative_to("/a"))
print(Path("/a/b/c.txt").is_relative_to("/a/b"))
print(Path("/a/b/../c").resolve())
print(Path("~").expanduser() == Path.home())
```
```text
False
True
sub/file.txt
b/c.txt
True
/a/c
True
```

`resolve()` makes a path absolute against the **current working directory** and removes `..` and symbolic links. `relative_to(base)` removes a prefix (and raises `ValueError` if the path is not inside `base`); `is_relative_to` answers `True` or `False`. `Path.cwd()` is the working directory, `Path.home()` is your home folder, `expanduser()` turns `~` into it.

A trick for "where is my script?": `Path(__file__).resolve().parent` is the folder of the current Python file, wherever you started it. Build data paths from it, and "file not found because of the working directory" goes away.

### 9.5 Doing things with paths

```python
from pathlib import Path

root = Path("demo")
(root / "a" / "b").mkdir(parents=True, exist_ok=True)
(root / "a" / "b").mkdir(parents=True, exist_ok=True)     # second time: fine
print(root.exists(), root.is_dir(), root.is_file())

note = root / "a" / "note.txt"
note.write_text("hello\nworld\n", encoding="utf-8")
print(note.read_text(encoding="utf-8").splitlines())
print(note.stat().st_size, "bytes")
(root / "a" / "blob.bin").write_bytes(b"\x00\x01\x02")
print((root / "a" / "blob.bin").read_bytes())

with note.open("a", encoding="utf-8") as f:
    f.write("more\n")
print(len(note.read_text().splitlines()))

(root / "empty.txt").touch()
print((root / "empty.txt").stat().st_size)

try:
    (root / "a").mkdir()
except FileExistsError as e:
    print("FileExistsError:", e)
```
```text
True True False
['hello', 'world']
12 bytes
b'\x00\x01\x02'
3
0
FileExistsError: [Errno 17] File exists: 'demo/a'
```

- `exists()`, `is_file()`, `is_dir()` ask the disk.
- `mkdir(parents=True, exist_ok=True)` creates a folder **and** missing parents, and is happy if it exists. Without `exist_ok=True` the second call raises `FileExistsError`, as the last line shows.
- `write_text(text, encoding=...)` / `read_text(encoding=...)` open, write or read, and close, in one line; `write_bytes` / `read_bytes` do the same for binary data. They are ideal for **small** files; for big files use `open()` and loops.
- `p.open("a", encoding="utf-8")` equals `open(p, "a", encoding="utf-8")`. Anything that accepts a path string accepts a `Path`.
- `touch()` creates an empty file; `stat().st_size` is the size in bytes.

### 9.6 Listing and searching

```python
from pathlib import Path

root = Path("proj")
for name in ["main.py", "notes.txt", "src/app.py", "src/deep/x.py", "src/data.csv"]:
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("x")

print("iterdir:", sorted(p.name for p in root.iterdir()))
print("glob *.py:", sorted(str(p) for p in root.glob("*.py")))
print("rglob *.py:", sorted(str(p) for p in root.rglob("*.py")))
print("only dirs:", sorted(p.name for p in root.rglob("*") if p.is_dir()))
```
```text
iterdir: ['main.py', 'notes.txt', 'src']
glob *.py: ['proj/main.py']
rglob *.py: ['proj/main.py', 'proj/src/app.py', 'proj/src/deep/x.py']
only dirs: ['deep', 'src']
```

- `iterdir()` lists the **direct** children, in **no guaranteed order**.
- `glob("*.py")` matches names in one folder: `*` is any characters (not `/`), `?` is one character.
- `rglob("*.py")` equals `glob("**/*.py")`: the folder **and all folders below** (`**` means "any number of folders").
- Both return **generators**, so a huge tree is not loaded at once. We used `sorted` only for a stable display.
- For only folders, filter with `is_dir()`. Python 3.12 added `Path.walk()`, the `pathlib` form of `os.walk`: for each folder it gives the folder, its sub-folder names and its file names.

Paths sort like strings: `file10.txt` comes before `file2.txt`, because `1` is smaller than `2`. Sort with a key if numbers matter.

### 9.7 `stat()`: size and time

`p.stat()` gives `st_size` (bytes) and `st_mtime`, the modification time in **seconds since 1 January 1970** (the Unix epoch), as a float.

Convert with `datetime.fromtimestamp(ts, tz=timezone.utc)`; without a time zone the answer depends on the computer. On Linux, `st_ctime` is **not** the creation time (it is the last metadata change), so do not use it as a "created" date.

### 9.8 Renaming and deleting

`rename(target)` moves or renames and returns the new `Path`. `unlink()` deletes a file (`missing_ok=True` ignores a file that is already gone). `rmdir()` deletes an **empty** folder and raises `OSError: [Errno 39] Directory not empty` otherwise. Folders with content need `shutil.rmtree`, which is dangerous (section 10).

### 9.9 Predict the output

**Predict the output.** Be careful with `suffix`, `parents` and the last line.

```python
from pathlib import Path

p = Path("/data/exports/2026/sales.report.CSV")
print(p.name)
print(p.stem)
print(p.suffix)
print(p.parent.name)
print(p.with_suffix(".json"))
print(p.parents[1])
print(p.suffix.lower() == ".csv")
print(Path("a") / "b" / "../c.txt")
```
<details><summary>Answer</summary>

```text
sales.report.CSV
sales.report
.CSV
2026
/data/exports/2026/sales.report.json
/data/exports
True
a/b/../c.txt
```


`name` is the last piece, `sales.report.CSV`. `stem` removes only the last suffix, so `sales.report` stays. `suffix` is `.CSV` (case kept). `p.parent.name` is `2026`. `with_suffix(".json")` replaces only the last suffix. `p.parents[0]` is `/data/exports/2026`, so `parents[1]` is `/data/exports`. And `Path("a") / "b" / "../c.txt"` keeps the `..` as text: `pathlib` does **not** simplify it unless you call `resolve()`.
</details>

## 10. `os`, `shutil` and `glob`

`pathlib` covers many tasks, but older code uses `os` and `os.path`, and some jobs (copying trees, archives) belong to `shutil`. You must be able to read all of them.

### 10.1 The `os` module

```python
import os
os.makedirs("a/b", exist_ok=True)
for name in ["a/one.txt", "a/b/two.txt"]:
    with open(name, "w") as f:
        f.write(name)
print(sorted(os.listdir("a")))
for folder, dirs, files in os.walk("a"):
    print(folder, sorted(dirs), sorted(files))
print(os.path.join("a", "b", "x.txt"), os.path.splitext("archive.tar.gz"))
print(os.path.basename("/x/y/z.txt"), os.path.dirname("/x/y/z.txt"))
```
```text
['b', 'one.txt']
a ['b'] ['one.txt']
a/b [] ['two.txt']
a/b/x.txt ('archive.tar', '.gz')
z.txt /x/y
```

| `os` call | `pathlib` form |
|---|---|
| `os.listdir(p)` | `Path(p).iterdir()` (names versus `Path` objects) |
| `os.makedirs(p, exist_ok=True)` | `Path(p).mkdir(parents=True, exist_ok=True)` |
| `os.path.join(a, b)` | `Path(a) / b` |
| `os.path.splitext(name)` | `Path(name).stem` and `.suffix` |
| `os.path.exists(p)` / `getsize(p)` | `Path(p).exists()` / `.stat().st_size` |
| `os.walk(p)` | `Path(p).walk()` (3.12+) |
| `os.remove(p)` | `Path(p).unlink()` |

`os.walk` gives (folder, sub-folders, files) triples. `os.path` functions work on **strings** and return strings. Things only `os` offers: `os.environ` (a dict of strings; use `.get(name, default)`, because indexing a missing variable raises `KeyError`), `os.replace`, `os.fsync`, `os.chmod`, `os.utime`, and `os.scandir`, a fast listing whose entries already know if they are files (use it for folders with many thousands of files).

### 10.2 `shutil`: copy, move, delete trees

`shutil` ("shell utilities") does the bigger jobs.

- `shutil.copy(src, dst)` copies content and permissions; if `dst` is an existing **folder**, the file goes inside with the same name. `shutil.copy2` also keeps the modification time: use it for backups.
- `shutil.copytree(src, dst)` copies a folder; `dst` must **not exist**, unless you pass `dirs_exist_ok=True`.
- `shutil.disk_usage(".")` gives `total`, `used`, `free` bytes (machine-specific). `shutil.which("python3")` finds a program on the `PATH`.
- `shutil.make_archive("backup", "zip", root_dir="data")` makes a ZIP of a folder; `unpack_archive` extracts it. (Extract archives only from sources you trust.)

**Moving:** `shutil.move(src, dst)` works across disks too (it copies, then deletes). When `dst` is a folder that already has a file with that name, you get `shutil.Error: Destination path 'archive/b.txt' already exists` and nothing is overwritten. Give the full new name to move **and** rename at once. Compare `os.replace`, which overwrites without asking: pick the one that fits your intention. Our organiser project uses `move`.

**Deleting a folder tree. Warning.** `shutil.rmtree(path)` deletes the folder and **everything inside it**, with no confirmation, no recycle bin and no undo. Programs run with a wrong variable (an empty string, a parent folder) have deleted whole home folders. Habits that protect you:

1. Print the path first, or ask for confirmation, or support a `--dry-run` option (you will build one in the project).
2. Never build the path from user input without checking it, for example with `is_relative_to`.
3. When testing, use only folders made by `tempfile.TemporaryDirectory()`.
4. `ignore_errors=True` hides problems. Use it only when you really do not care.

### 10.3 `glob`: finding files by pattern

The `glob` module finds paths with shell-like patterns. It returns **strings**; `Path.glob` returns `Path` objects. The rules are the same.

```python
import glob
from pathlib import Path
for name in ["a.txt", "b.txt", "ab.txt", "c.csv", "d1.log", ".hidden.txt", "sub/e.txt", "sub/deep/f.txt"]:
    p = Path(name); p.parent.mkdir(parents=True, exist_ok=True); p.write_text("x")

print(sorted(glob.glob("*.txt")))
print(sorted(glob.glob("?.txt")))
print(sorted(glob.glob("*.[tc]*")))
print(sorted(glob.glob("**/*.txt", recursive=True)))
print(sorted(glob.glob("**/*.txt")))
print(sorted(glob.glob(".*.txt")))
```
```text
['a.txt', 'ab.txt', 'b.txt']
['a.txt', 'b.txt']
['a.txt', 'ab.txt', 'b.txt', 'c.csv']
['a.txt', 'ab.txt', 'b.txt', 'sub/deep/f.txt', 'sub/e.txt']
['sub/e.txt']
['.hidden.txt']
```

| Pattern | Matches |
|---|---|
| `*` | any number of characters (not `/`) |
| `?` | exactly one character |
| `[12]`, `[a-z]` | one character from a set or a range |
| `**` with `recursive=True` | any number of folders |

Traps in this output:

- **Hidden files** (names starting with a dot) are **not** matched by `*`. Only a pattern that starts with a dot, like `.*.txt`, finds them.
- Without `recursive=True`, `**` acts like a plain `*`: `**/*.txt` found only `sub/e.txt`, one folder deep. With `recursive=True` it also found `sub/deep/f.txt` and the files in the current folder.
- A pattern with no match gives an **empty list**, not an error.
- The **order is not guaranteed**: use `sorted(...)`.

`glob.iglob` is the lazy version for huge trees. `fnmatch.fnmatch(name, pattern)` applies the same patterns to names you already have; it follows the operating system's case rules (`"report.TXT"` does not match `"*.txt"` on Linux but does on Windows), and `fnmatchcase` is always case-sensitive.

### 10.4 Which tool to use?

- **`pathlib`** for paths, listing, small reads and writes, renaming.
- **`shutil`** for copy, move, tree copy, tree delete, archives.
- **`os`** for what `pathlib` lacks (environment, `replace`, `fsync`, `chmod`, `utime`), and for reading older code.
- **`glob`** for patterns on strings; otherwise `Path.glob`.


## 11. CSV files

### 11.1 What CSV is, and why not `split(",")`

**CSV** (comma-separated values) is the simplest format for tables: one row per line, columns separated by commas. Spreadsheets and databases export it. It looks so simple that beginners write `line.split(",")`, which breaks on real data. Real CSV can contain commas **inside** a value (`Asha,"likes tea, and coffee"`), quote characters, **line breaks** and empty values. The `csv` module handles all of them. Always use it.

### 11.2 Writing and reading

```python
import csv

rows = [["name", "qty", "price"], ["pen", 10, 2.5], ["notebook", 3, 40]]
with open("items.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(rows[0])
    writer.writerows(rows[1:])
print(open("items.csv", "rb").read())

with open("items.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    print(header)
    for row in reader:
        print(row, type(row[1]).__name__)
```
```text
b'name,qty,price\r\npen,10,2.5\r\nnotebook,3,40\r\n'
['name', 'qty', 'price']
['pen', '10', '2.5'] str
['notebook', '3', '40'] str
```

`newline=""` is **required** when you open a CSV file (11.5 explains why). The writer converts numbers with `str`, and `writerows` takes any iterable of rows. The default line ending of the module is `\r\n` (the CSV standard).

The second half reads the file back. `csv.reader(f)` is **lazy**: one row (a list of strings) at a time, so you can stream a huge CSV like any file (section 7). `next(reader)` takes the header. **Every value is a string**: `'10'`, not `10`. You must convert with `int()` and `float()`. Forgetting this is the number one CSV bug.

### 11.3 `DictReader` and `DictWriter`

A list of strings is fragile: if the column order changes, `row[2]` points to the wrong thing. `DictReader` uses the header to give each row as a dictionary:

```python
import csv

with open("items.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print(reader.fieldnames)
    for row in reader:
        print(row)
        print(row["name"], int(row["qty"]) * float(row["price"]))

people = [{"name": "Asha", "city": "Pune"}, {"name": "Ravi", "city": "Delhi"}]
with open("people.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "city"])
    writer.writeheader()
    writer.writerows(people)
print(open("people.csv", newline="").read().splitlines())
```
```text
['name', 'qty', 'price']
{'name': 'pen', 'qty': '10', 'price': '2.5'}
pen 25.0
{'name': 'notebook', 'qty': '3', 'price': '40'}
notebook 120.0
['name,city', 'Asha,Pune', 'Ravi,Delhi']
```

`reader.fieldnames` is the header; `row["price"]` does not depend on the column order. `DictWriter` needs `fieldnames`, and `writeheader()` writes them. Two more facts for files from other people: a row that is **too short** gets `None` for the missing columns; a row that is **too long** puts the extra values in a **list under the key `None`**. A `DictWriter` refuses a row with keys that are not in `fieldnames` (`ValueError`), unless you pass `extrasaction="ignore"`.

### 11.4 Quoting: the module does the hard part

```python
import csv, io

rows = [
    ["Asha", "likes tea, and coffee"],
    ["Ravi", 'says "hello"'],
    ["Meena", "two\nlines"],
    ["Zoya", ""],
    ["Omar", None],
]
buffer = io.StringIO(newline="")
csv.writer(buffer).writerows(rows)
print(repr(buffer.getvalue()))

buffer.seek(0)
for row in csv.reader(buffer):
    print(row)
```
```text
'Asha,"likes tea, and coffee"\r\nRavi,"says ""hello"""\r\nMeena,"two\nlines"\r\nZoya,\r\nOmar,\r\n'
['Asha', 'likes tea, and coffee']
['Ravi', 'says "hello"']
['Meena', 'two\nlines']
['Zoya', '']
['Omar', '']
```

- A value with a comma, a quote or a line break is wrapped in double quotes, and inner quotes are **doubled**.
- The line break inside a value stayed inside the quotes, and the reader returned it as one value, `'two\nlines'`.
- `None` and `""` both become an empty field and come back as `''`. CSV cannot tell "missing" from "empty".
- Options: `delimiter="\t"` (TSV files) or `";"` (European Excel); `quoting=csv.QUOTE_ALL`; `lineterminator="\n"`.
- `csv.writer` works with **any file-like object**: a file, `io.StringIO` (as here) or even `sys.stdout`.

### 11.5 The `newline=""` trap

The `csv` module handles line endings itself, including line breaks **inside** quoted values. If the file object also translates line endings (the text-mode default), the two layers fight. On Windows, writing without `newline=""` gives blank lines between the rows. We can simulate Windows with `newline="\r\n"`:

```python
import csv

rows = [["a", "b"], ["1", "2"]]

with open("good.csv", "w", newline="") as f:
    csv.writer(f).writerows(rows)

# Windows-style text mode simulated with newline="\r\n":
with open("bad.csv", "w", newline="\r\n") as f:
    csv.writer(f).writerows(rows)

print("with newline='' :", open("good.csv", "rb").read())
print("without it (on Windows):", open("bad.csv", "rb").read())
```
```text
with newline='' : b'a,b\r\n1,2\r\n'
without it (on Windows): b'a,b\r\r\n1,2\r\r\n'
```

Without `newline=""`, the writer's `\r\n` was converted **again**, giving `\r\r\n`, which many programs show as an empty line after each row. When reading, the same rule protects line breaks inside values: with `newline=""` the reader sees the original characters. On Linux you may not notice a bug for a long time; on Windows it shows at once. **Rule: `open(path, newline="", encoding="utf-8")` for every CSV file, reading and writing.**

### 11.6 CSV and big files

Because `csv.reader` and `DictReader` are lazy, you can process millions of rows in constant memory. Total the sales per city by streaming into a dictionary, and only the totals stay in memory:

```python
totals = {}
with open("sales.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        city = row["city"]
        totals[city] = totals.get(city, 0) + int(row["amount"])
```

Do not write `list(csv.DictReader(f))` for big files.

### 11.7 Predict the output

**Predict the output.** Remember: every value from a CSV is a string.

```python
import csv, io

text = "name,score\nAsha,9\nRavi,10\nMeena,100\n"
rows = list(csv.DictReader(io.StringIO(text)))
print(max(r["score"] for r in rows))
print(max(int(r["score"]) for r in rows))
print(rows[0]["score"] + rows[1]["score"])
print(sorted(r["score"] for r in rows))
```
<details><summary>Answer</summary>

```text
9
100
910
['10', '100', '9']
```


`max` on **strings** compares character by character, and `"9"` is bigger than `"10"` and `"100"` because `"9" > "1"`. So the first line is `9`, which is wrong for numbers. With `int` we get `100`. Adding two strings **joins** them: `"9" + "10"` is `"910"`. The sorted strings are in text order. Convert early, when you read the row.
</details>

## 12. JSON files

### 12.1 What JSON is

**JSON** is the standard format for data exchange: web APIs, configuration, saved data. It is readable text, and every language can read it. It maps almost directly to Python's basic types:

| JSON | Python |
|---|---|
| object `{...}` | `dict` |
| array `[...]` | `list` |
| string | `str` |
| number | `int` or `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

The module `json` has `dumps`/`loads` (to and from **strings**) and `dump`/`load` (to and from **file objects**).

```python
import json

data = {"name": "Asha", "age": 21, "marks": [90, 85.5], "active": True, "address": None}
text = json.dumps(data)
print(text)
back = json.loads(text)
print(back == data, back is data)
print(json.dumps({"b": 1, "a": [1, 2]}, indent=2, sort_keys=True))
print(json.dumps(data, separators=(",", ":")))
```
```text
{"name": "Asha", "age": 21, "marks": [90, 85.5], "active": true, "address": null}
True False
{
  "a": [
    1,
    2
  ],
  "b": 1
}
{"name":"Asha","age":21,"marks":[90,85.5],"active":true,"address":null}
```

- The round trip gives an **equal** but **new** object (`back is data` is `False`).
- `indent=2` makes the text pretty; `sort_keys=True` makes the key order stable (good for files under version control); `separators=(",", ":")` makes the smallest text.
- JSON writes `true` and `null`; Python writes `True` and `None`.

For files: `json.dump(obj, f, indent=2)` and `json.load(f)`, with `encoding="utf-8"` on the `open` (the JSON standard says UTF-8). For a settings file that must never be corrupted, write it with the atomic recipe of section 8.

### 12.2 What JSON cannot keep

JSON has fewer types than Python, so a round trip can lose information:

```python
import json

data = {"tuple": (1, 2), "int_key": {1: "one", 2: "two"}, "t": True, "n": None, "f": 1.0}
text = json.dumps(data)
print(text)
back = json.loads(text)
print(back["tuple"], type(back["tuple"]).__name__)
print(back["int_key"])
print(json.loads("[1, 2.0, \"3\", true, null]"))
print(json.dumps("café ₹"), json.dumps("café ₹", ensure_ascii=False))
```
```text
{"tuple": [1, 2], "int_key": {"1": "one", "2": "two"}, "t": true, "n": null, "f": 1.0}
[1, 2] list
{'1': 'one', '2': 'two'}
[1, 2.0, '3', True, None]
"caf\u00e9 \u20b9" "café ₹"
```

- A **tuple** becomes a list.
- **Keys must be strings**: the integer keys became `"1"` and `"2"`, and come back as strings.
- By default, non-ASCII characters are written as `\uXXXX`. That is valid but unreadable. `ensure_ascii=False` keeps `café ₹` (then write the file with `encoding="utf-8"`).
- JSON has no `set`, `bytes`, dates or `Path`.

### 12.3 When the JSON is broken

`json.loads('{"a": 1,}')` raises `json.JSONDecodeError`, a subclass of `ValueError`. The error carries a message, the line and the column (`e.msg`, `e.lineno`, `e.colno`). A trailing comma and single quotes are the two most common mistakes of people who write JSON by hand: JSON is **stricter** than Python. In a tool, show the message to the user; it is a user error, not a crash.

### 12.4 Types JSON does not know: `default=`

```python
import json
from datetime import date, datetime
from pathlib import Path

try:
    json.dumps({"tags": {"a", "b"}})
except TypeError as e:
    print("TypeError:", e)

def encode_extra(obj):
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"cannot serialise {type(obj).__name__}")

record = {"tags": {"b", "a"}, "when": datetime(2026, 1, 15, 9, 30), "where": Path("/data/x.csv")}
text = json.dumps(record, default=encode_extra)
print(text)
back = json.loads(text)
print(type(back["when"]).__name__, datetime.fromisoformat(back["when"]).year)
```
```text
TypeError: Object of type set is not JSON serializable
{"tags": ["a", "b"], "when": "2026-01-15T09:30:00", "where": "/data/x.csv"}
str 2026
```

`json.dumps(obj, default=function)` calls your function for each object it cannot handle. It must return something JSON can store, or raise `TypeError`. The decoder does not know our choices, so `"when"` came back as a **string**; converting it back (`datetime.fromisoformat`) is your job. The rule: **decide a representation** (ISO 8601 text for dates, a sorted list for sets), write the encoder, and write the matching decoding code.

### 12.5 JSON Lines: JSON you can stream

A normal JSON file is **one** value, so `json.load` needs it all in memory. For long lists of records (events, log entries), use **JSON Lines** (`.jsonl`): **one JSON value per line**.

```python
import json

events = [{"id": 1, "kind": "login"}, {"id": 2, "kind": "click"}, {"id": 3, "kind": "logout"}]
with open("events.jsonl", "w", encoding="utf-8") as f:
    for event in events:
        f.write(json.dumps(event) + "\n")
print(open("events.jsonl").read(), end="")

with open("events.jsonl", encoding="utf-8") as f:
    for line in f:
        event = json.loads(line)
        if event["kind"] != "click":
            print(event["id"], event["kind"])
```
```text
{"id": 1, "kind": "login"}
{"id": 2, "kind": "click"}
{"id": 3, "kind": "logout"}
1 login
3 logout
```

Write with `f.write(json.dumps(event) + "\n")` (`dumps` never puts a raw newline inside a value). Read with `for line in f: json.loads(line)`. You get the constant-memory streaming of section 7, and easy appending with `"a"`. Many logging and data tools use this format.

### 12.6 Predict the output

**Predict the output.** Look at the key `3` and the tuple.

```python
import json

data = {"a": (1, 2), 3: "three", "ok": True, "none": None}
text = json.dumps(data)
print(text)
back = json.loads(text)
print(back == data)
print(sorted(back, key=str))
print(back["a"])
```
<details><summary>Answer</summary>

```text
{"a": [1, 2], "3": "three", "ok": true, "none": null}
False
['3', 'a', 'none', 'ok']
[1, 2]
```


The tuple becomes a list, the integer key `3` becomes the string `"3"`, `True` becomes `true`, `None` becomes `null`. After `loads` the keys are `'a'`, `'3'`, `'ok'`, `'none'`, so `sorted(back, key=str)` gives `['3', 'a', 'none', 'ok']`. The original has the integer key `3` and a tuple, so `back == data` is `False`: the round trip is **not exact**.
</details>

## 13. TOML and `configparser`

Programs need **settings**: a port, a folder name, a debug switch. Settings should live in a file that a human edits, not inside the code. Two formats are in the standard library.

### 13.1 TOML with `tomllib`

**TOML** is a clear, human-friendly format. Python itself uses it (`pyproject.toml`). Unlike INI, TOML has **real types**: strings, integers, floats, booleans, dates, lists and nested tables. The module `tomllib` (Python 3.11+) **reads** TOML.

```python
import tomllib

text = """
title = "My app"
debug = false
port = 8080
created = 2026-01-15

[database]
host = "localhost"
ports = [5432, 5433]

[[servers]]
name = "alpha"

[[servers]]
name = "beta"
"""
config = tomllib.loads(text)
print(config["title"], config["port"], config["debug"])
print(config["created"], type(config["created"]).__name__)
print(config["database"])
print([s["name"] for s in config["servers"]])
```
```text
My app 8080 False
2026-01-15 date
{'host': 'localhost', 'ports': [5432, 5433]}
['alpha', 'beta']
```

- `[database]` starts a **table**, a dict inside the dict (`[database.credentials]` would make a table inside a table).
- `[[servers]]` (double brackets) is an **array of tables**: each block adds one dict to a list.
- Types are real: `8080` is an `int`, `false` is `False`, `2026-01-15` is a `datetime.date`. Strings need quotes: `name = "demo"`.

For files use **binary mode** (`"rb"`), because TOML is defined as UTF-8 and the library decodes it itself:

```python
with open("app.toml", "rb") as f:
    config = tomllib.load(f)
```

`tomllib.load` raises a clear `TypeError` ("File must be opened in binary mode") for a text-mode file, and `tomllib.TOMLDecodeError` for a syntax error (with line and column). And `hasattr(tomllib, "dump")` is `False`: **`tomllib` only reads**. A common design is that users edit the TOML by hand and your program only reads it; if your program must save data, use JSON. A good pattern is to start from a `DEFAULTS` dict and `update` it with the user's file, ignoring `FileNotFoundError`.

### 13.2 `configparser` (INI files)

The **INI** format is older and simpler: sections in `[brackets]` and `key = value` lines. The module `configparser` reads and writes it.

```python
import configparser

text = """
[DEFAULT]
timeout = 30

[server]
host = example.org
port = 8080
debug = yes

[client]
timeout = 10
"""
config = configparser.ConfigParser()
config.read_string(text)
print(config.sections())
print(config["server"]["host"], type(config["server"]["port"]).__name__)
print(config.getint("server", "port") + 1, config.getboolean("server", "debug"))
print(config["server"].getint("timeout"), config["client"].getint("timeout"))
print(config.get("server", "missing", fallback="none"))
```
```text
['server', 'client']
example.org str
8081 True
30 10
none
```

- **All values are strings.** Use `getint`, `getfloat` and `getboolean` (which understands `yes/no`, `true/false`, `on/off`, `1/0`).
- Values in `[DEFAULT]` apply to **every** section unless the section sets its own: `server` took `timeout = 30`, `client` has `10`.
- `fallback=...` gives a value for a missing key instead of raising an error.
- `config.write(f)` writes INI text; `config.read(path)` **returns the list of files it read** and does **not** raise an error for a missing file, so check the result if you need the file.
- Keys are **case-insensitive**; section names are case-sensitive.
- `%` is special (interpolation, `%(name)s`): a value such as `50%` raises `InterpolationSyntaxError`. Create the parser with `ConfigParser(interpolation=None)` if you do not need it.

### 13.3 Which format?

| Need | Choose |
|---|---|
| Hand-edited settings with types and nesting | **TOML** |
| Simple flat settings, old tools | INI (`configparser`) |
| Data to or from programs and web APIs | **JSON** |
| A table of rows | **CSV** |
| A big stream of records | JSON Lines or CSV |
| Python objects, only for yourself | pickle (read the next section first) |

## 14. `pickle` and its risks

### 14.1 What pickle does

`pickle` saves almost **any Python object** to bytes and loads it back, with its types intact.

```python
import pickle

data = {"scores": [90, 85], "pair": (1, 2), "tags": {"a", "b"}, "none": None}
blob = pickle.dumps(data)
print(type(blob).__name__, blob[:2])
back = pickle.loads(blob)
print(back == data)
print(type(back["pair"]).__name__, type(back["tags"]).__name__)

with open("state.pkl", "wb") as f:
    pickle.dump(data, f)
with open("state.pkl", "rb") as f:
    print(pickle.load(f)["scores"])
```
```text
bytes b'\x80\x05'
True
tuple set
[90, 85]
```

`dumps`/`loads` work with bytes; `dump`/`load` work with files opened in binary mode (`"wb"`, `"rb"`). Unlike JSON, nothing was lost: the tuple is still a `tuple` and the set is still a `set`. It looks perfect for saving a program's state. But it has three serious weaknesses.

### 14.2 Three weaknesses

1. **Python only.** The format is binary and Python-specific, and it changes between versions. An object saved by one version of your code may not load in a later version. It is not a format for long-term storage.
2. **Some things cannot be pickled**: lambdas, open files, network connections. `pickle.dumps(lambda x: x)` raises `PicklingError`, and pickling a file object raises `TypeError`.
3. **Loading a pickle can run code.** This is the important one.

### 14.3 Unpickling can call any function

A pickle is not just data; it is a small **program** for a stack machine, and one instruction says "import this function and call it with these arguments". If you `pickle.load` a file that somebody else prepared, that person decides what runs on your computer, with your permissions: reading your files, deleting them, installing a back door.

To show this with a **harmless** payload, we write a pickle by hand that tells Python to call the built-in `print` when it is loaded. (`pickletools.dis` shows the instructions without running them.)

```python
import pickle, pickletools

evil = b"cbuiltins\nprint\n(Vhello, I was run just by loading!\ntR."
pickletools.dis(evil)
result = pickle.loads(evil)
print("loads returned:", result)
```
```text
    0: c    GLOBAL     'builtins print'
   16: (    MARK
   17: V        UNICODE    'hello, I was run just by loading!'
   52: t        TUPLE      (MARK at 16)
   53: R    REDUCE
   54: .    STOP
highest protocol among opcodes = 0
hello, I was run just by loading!
loads returned: None
```

Read the disassembly: `GLOBAL 'builtins print'` fetches the function; `MARK`, the text and `TUPLE` build the argument list; `REDUCE` **calls** `print(...)`. The message was printed **just by loading**, and `loads` returned `None`, the result of `print`. A malicious file would name a dangerous function instead of `print`. We will not show that, but you now understand how it works.

The rules:

1. **Never unpickle data from a source you do not fully trust**: a download, an email attachment, a network message, a user upload, a file in a folder others can write to. You cannot check a pickle by looking at it.
2. Never use pickle across a trust boundary. Use **JSON**, CSV or TOML: loading them can never run code.
3. If you use pickle for your own files (a cache on your own disk), keep them where only you can write, and treat them as disposable.
4. There is a way to restrict what an unpickler may load (a `find_class` method in a subclass of `pickle.Unpickler`), but it needs classes (core.14), and the documentation still advises JSON for untrusted data.
5. `shelve` and many machine-learning model files (`.pkl`, `.pt`) use pickle inside. The same warning applies to **downloaded models**.

**Summary: pickle is a convenience for your own temporary data. For everything else, use JSON.**

## 15. `tempfile`: temporary files

### 15.1 Why temporary files

Sometimes you need a file or folder for a short time: a scratch area for a test, an intermediate result, the temp file of section 8. If you invent a name such as `temp.txt`, two runs can clash, someone may guess it, and nobody cleans up. The `tempfile` module creates **uniquely named** files and folders safely, and can delete them for you.

```python
import os, tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as folder:
    work = Path(folder)
    (work / "a.txt").write_text("scratch")
    print(sorted(p.name for p in work.iterdir()), work.exists())
print(work.exists())

with tempfile.NamedTemporaryFile("w+", suffix=".txt", encoding="utf-8") as tmp:
    tmp.write("hello temp")
    tmp.flush()
    tmp.seek(0)
    print(tmp.read(), os.path.exists(tmp.name))
print(os.path.exists(tmp.name))
```
```text
['a.txt'] True
False
hello temp True
False
```

- `TemporaryDirectory()` is a context manager. It creates an empty folder; when the `with` block ends, the folder and **everything inside** is deleted. It is the right tool for tests and scratch work.
- `NamedTemporaryFile("w+")` creates a file with a visible name; with `delete=True` (the default) it is deleted when closed. `"w+"` means read **and** write in text mode, and creates the file. We called `flush()` before using the name and `seek(0)` before reading. (On Windows you cannot open it a second time while it is open; use `delete=False` or a temporary folder.)
- `TemporaryFile` has **no name** on most systems, so no other program can find it. `mkstemp` and `mkdtemp` return a path (and, for `mkstemp`, a low-level number) and **you** must remove them; section 8 used `mkstemp`.
- `tempfile.gettempdir()` is the system's temporary folder (`/tmp` on Linux). All functions accept `dir=`, `prefix=` and `suffix=`.

A test that touches the disk should never use real data folders: give each test a fresh `TemporaryDirectory`. Nothing is left afterwards, even if the test fails. The organiser project uses this idea.


## 16. Standard streams: stdin, stdout, stderr

### 16.1 Three streams that every program has

When a program starts, the operating system gives it three **ready-made open files**:

| Stream | Python name | Default | Used for |
|---|---|---|---|
| standard input | `sys.stdin` | the keyboard | data coming **in** |
| standard output | `sys.stdout` | the screen | the normal **results** |
| standard error | `sys.stderr` | the screen | **errors** and warnings |

`print()` writes to `sys.stdout`; `input()` reads from `sys.stdin`. They are ordinary text file objects: you can iterate over `sys.stdin`, call `.write()` on `sys.stdout`, and pass them to `print(file=...)` or `csv.writer`.

Why **two** output streams? Because a user often **redirects** the results to a file or into another program, and then error messages must **not** be mixed into the results. In a shell:

```text
python tool.py > result.txt      # stdout goes to a file; errors still on screen
python tool.py 2> errors.txt     # stderr goes to a file
python tool.py < input.txt       # stdin comes from a file
python tool.py | sort            # stdout of tool becomes stdin of sort
```

A well-behaved tool writes results to stdout, and everything else (progress, warnings, errors) to stderr.

### 16.2 Reading standard input

```python
import sys

count = 0
for line in sys.stdin:
    count += 1
    print(count, line.rstrip("\n").upper())
print("lines:", count)
```
```text
$ python std_stdin.py
1 RED
2 GREEN
3 BLUE
lines: 3
```

The three lines were given to the program as its standard input (as if you had used `python std_stdin.py < colours.txt`). Iterating `sys.stdin` works like iterating a file: lazy, line by line, so your tool can process an endless stream, such as the output of another program. `sys.stdin.read()` reads everything at once. `input(prompt)` reads **one line** without the newline, and raises `EOFError` when there is no more input (`Ctrl+D` on Linux and macOS, `Ctrl+Z` then Enter on Windows, or a finished pipe). For tools used in pipelines, prefer `for line in sys.stdin`.

A **filter** reads stdin and writes stdout, and small filters can be chained with `|`. This one drops blank lines and comments and shouts the rest:

```python
import sys

for line in sys.stdin:
    line = line.strip()
    if line and not line.startswith("#"):
        print(line.upper())
```

It works on any file size, because of streaming (section 7).

### 16.3 stdout and stderr

```python
import sys
print("normal message")
print("warning: something odd", file=sys.stderr)
sys.stdout.write("no newline added")
sys.stdout.write("\n")
sys.stderr.write("error: stderr write\n")
print(sys.stdout.name, sys.stderr.name, sys.stdin.name)
```
```text
$ python std_out_err.py
[stdout]
normal message
no newline added
<stdout> <stderr> <stdin>
[stderr]
warning: something odd
error: stderr write
```

Here the runner shows the two streams **separately**; in your terminal they appear together, in order of writing. `sys.stdout.write(text)` is `print` without the automatic newline. The names `<stdout>`, `<stderr>`, `<stdin>` are the `name` attributes of the three file objects. `print("...", file=sys.stderr)` is the usual way to report problems: if you redirect stdout to a file, the warnings still reach the screen.

`isatty()` tells whether a stream is a real terminal (programs use it to decide about colours). When stdout is **not** a terminal, it is **buffered**, so messages may arrive late or out of order relative to stderr; use `print(..., flush=True)` for progress messages. `sys.stdin.buffer` and `sys.stdout.buffer` are the **binary** versions, for programs that handle bytes.

### 16.4 Capturing output in code and tests

Because the streams are file objects, you can **replace** them. `io.StringIO` is a file-like object that keeps text in memory (`import io`). `contextlib.redirect_stdout` points `sys.stdout` to an object during its block.

```python
import io
from contextlib import redirect_stdout

buffer = io.StringIO()
with redirect_stdout(buffer):
    print("hidden from the screen")
print("captured:", repr(buffer.getvalue()))     # captured: 'hidden from the screen\n'
```

This is how you **test** programs that print. You can also write a function with an `out` parameter (default `sys.stdout`) and use `print(..., file=out)`, so a test can pass a `StringIO`. `io.StringIO("10\n20\n")` also works as a fake input file.

### 16.5 `sys.argv` and exit codes

The command line reaches your program as the list `sys.argv`: the script name first, then the arguments, all **strings**.

```python
import sys
print(sys.argv)
print(len(sys.argv))
for arg in sys.argv[1:]:
    print(repr(arg))
```
```text
$ python std_argv.py notes.txt 'two words' --flag
['std_argv.py', 'notes.txt', 'two words', '--flag']
4
'notes.txt'
'two words'
'--flag'
```

The shell splits the command line into words **before** Python sees it; quotes group words, so `'two words'` is one argument. Parsing by hand is fine for one argument, but it gets messy fast: that is why `argparse` exists.

When a program ends, it returns an **exit code** to the operating system: **0 means success**, anything else means failure. Shell scripts (`&&`), `make` and CI systems read it. `sys.exit(code)` ends the program with a code:

```python
import sys

def main():
    print("working...")
    if len(sys.argv) < 2:
        print("usage: tool.py NAME", file=sys.stderr)
        return 2
    print("hello", sys.argv[1])
    return 0

sys.exit(main())
```
```text
$ python std_exit.py
working...
usage: tool.py NAME
[exit code 2]
```

`sys.exit(2)` gives code 2 (the usual "wrong usage"); `sys.exit()` or reaching the end gives 0; `sys.exit("message")` prints the message to **stderr** and exits with code **1**. The usual layout is a `main()` function that **returns** the code, and `sys.exit(main())` at the end.

## 17. `argparse`: command-line tools

### 17.1 Why argparse

`sys.argv` is only a list of strings. A real tool needs positional arguments (`copy a.txt b.txt`), options with values (`--lines 5`), flags (`--verbose`), short and long names (`-n`, `--lines`), type conversion, defaults, a help text (`--help`), and **clear error messages** when the user makes a mistake. `argparse` does all of this and writes the help for you.

### 17.2 A first parser

```python
import argparse

parser = argparse.ArgumentParser(prog="head", description="Show the first lines of a file.")
parser.add_argument("filename", help="file to read")
parser.add_argument("-n", "--lines", type=int, default=10, help="how many lines (default: %(default)s)")
parser.add_argument("-v", "--verbose", action="store_true", help="say more")

args = parser.parse_args(["notes.txt", "-n", "5", "--verbose"])
print(args)
print(args.filename, args.lines, args.verbose)
print(parser.parse_args(["x.txt"]))
print(parser.parse_args(["--lines=3", "x.txt"]))
print(parser.parse_args(["-n7", "x.txt", "-v"]))
```
```text
Namespace(filename='notes.txt', lines=5, verbose=True)
notes.txt 5 True
Namespace(filename='x.txt', lines=10, verbose=False)
Namespace(filename='x.txt', lines=3, verbose=False)
Namespace(filename='x.txt', lines=7, verbose=True)
```

The steps are always the same: create `ArgumentParser(prog=..., description=...)`; call `add_argument(...)` for each argument; call `parse_args(argv)`, which returns a **Namespace**, an object with one attribute per argument. With no list, it reads `sys.argv[1:]`.

- A name **without dashes** (`"filename"`) is a **positional** argument: required, identified by its place.
- A name **with dashes** (`"-n"`, `"--lines"`) is an **option**: optional, identified by name. The attribute comes from the long name; dashes become underscores (`--dry-run` gives `args.dry_run`).
- `type=int` converts the text (and gives a clean error if that fails). `default=10` is used when the option is missing; without a default it is `None`.
- `action="store_true"` makes a **flag**: `False`, or `True` if present.
- Option values can be written `--lines 5`, `--lines=5`, `-n 5` or `-n5`.

### 17.3 The help text

```python
import argparse

parser = argparse.ArgumentParser(prog="head", description="Show the first lines of a file.")
parser.add_argument("filename", help="file to read")
parser.add_argument("-n", "--lines", type=int, default=10, metavar="N",
                    help="how many lines (default: %(default)s)")
parser.add_argument("--mode", choices=["fast", "safe"], default="safe", help="speed or safety")
parser.print_help()
```
```text
usage: head [-h] [-n N] [--mode {fast,safe}] filename

Show the first lines of a file.

positional arguments:
  filename            file to read

options:
  -h, --help          show this help message and exit
  -n, --lines N       how many lines (default: 10)
  --mode {fast,safe}  speed or safety
```

You get `--help` and `-h` for free. `%(default)s` in a help string prints the default, `metavar="N"` changes the placeholder, and `choices=[...]` shows as `{fast,safe}`. Writing good `help=` texts is part of the job: this is the manual of your tool.

### 17.4 Errors and exit codes: argparse does it for you

When the user makes a mistake, argparse prints the usage and a clear message to **stderr** and exits with code **2**. Here we catch `SystemExit` to see the code (the runner shows stdout and stderr separately):

```python
import argparse, sys

parser = argparse.ArgumentParser(prog="head")
parser.add_argument("filename")
parser.add_argument("-n", "--lines", type=int, default=10)
parser.add_argument("--mode", choices=["fast", "safe"], default="safe")

for argv in [[], ["x.txt", "-n", "abc"], ["x.txt", "--mode", "turbo"]]:
    print("argv:", argv)
    try:
        parser.parse_args(argv)
    except SystemExit as e:
        print("exit code:", e.code, file=sys.stdout, flush=True)
```
```text
$ python arg_errors.py
[stdout]
argv: []
exit code: 2
argv: ['x.txt', '-n', 'abc']
exit code: 2
argv: ['x.txt', '--mode', 'turbo']
exit code: 2
[stderr]
usage: head [-h] [-n LINES] [--mode {fast,safe}] filename
head: error: the following arguments are required: filename
usage: head [-h] [-n LINES] [--mode {fast,safe}] filename
head: error: argument -n/--lines: invalid int value: 'abc'
usage: head [-h] [-n LINES] [--mode {fast,safe}] filename
head: error: argument --mode: invalid choice: 'turbo' (choose from fast, safe)
```

Each mistake has its own message: a missing argument, a bad `int`, a choice that is not allowed. In your own tool you do **not** catch these; let the program stop. (In tests you catch `SystemExit`.)

### 17.5 Types, repeated options, counters

```python
import argparse
from pathlib import Path

def positive_int(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a whole number")
    if value <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not positive")
    return value

parser = argparse.ArgumentParser(prog="tool")
parser.add_argument("files", nargs="+", type=Path, help="one or more files")
parser.add_argument("--size", type=positive_int, default=1)
parser.add_argument("--tag", action="append", default=[])
parser.add_argument("-v", "--verbose", action="count", default=0)

print(parser.parse_args(["a.txt", "b.txt", "--size", "4", "--tag", "x", "--tag", "y", "-vv"]))
parser.parse_args(["a.txt", "--size", "0"])
```
```text
$ python arg_types.py
[stdout]
Namespace(files=[PosixPath('a.txt'), PosixPath('b.txt')], size=4, tag=['x', 'y'], verbose=2)
[stderr]
usage: tool [-h] [--size SIZE] [--tag TAG] [-v] files [files ...]
tool: error: argument --size: 0 is not positive
[exit code 2]
```

- `nargs="+"` means "one or more values" (`"*"` zero or more, `"?"` optional); with `type=Path` each value becomes a `Path`.
- A **custom type** is any function that takes the text and returns a value. It raises `argparse.ArgumentTypeError(message)` for bad input, and argparse shows it as a normal error: `argument --size: 0 is not positive`.
- `action="append"` lets the user repeat an option: `--tag x --tag y` gives `['x', 'y']`.
- `action="count"` counts a flag: `-vv` is 2, the usual way to make verbosity levels.
- `argparse.BooleanOptionalAction` makes a pair `--colour` / `--no-colour`.
- `nargs="?"` with a `default` makes a positional argument **optional**. A lone `--` means "everything after this is positional", so you can name a file `-weird-name.txt`.
- `parser.add_mutually_exclusive_group()` makes options that cannot be used together.

For rules that argparse cannot know (for example "low must not be bigger than high"), check the values yourself and call `parser.error(message)`. It prints the usage and message to stderr and exits with code 2, like any usage error.

### 17.6 Subcommands (briefly)

Tools like `git` have **subcommands** (`git add`, `git commit`). With `add_subparsers`, each subcommand gets its own parser and arguments:

```python
import argparse

parser = argparse.ArgumentParser(prog="notes")
sub = parser.add_subparsers(dest="command", required=True)
sub.add_parser("add", help="add a note").add_argument("text")
sub.add_parser("list", help="show notes").add_argument("--last", type=int, default=5)

print(parser.parse_args(["add", "buy milk"]))
print(parser.parse_args(["list", "--last", "2"]))
parser.parse_args([])
```
```text
$ python arg_subcommands.py
[stdout]
Namespace(command='add', text='buy milk')
Namespace(command='list', last=2)
[stderr]
usage: notes [-h] {add,list} ...
notes: error: the following arguments are required: command
[exit code 2]
```

`dest="command"` stores the chosen subcommand and `required=True` makes it mandatory. A common style is `sub.add_parser("add").set_defaults(func=do_add)` and then `args.func(args)`, instead of a long `if/elif` on `args.command` (functions as values, core.11).

### 17.7 The `main(argv)` pattern

The recommended layout of a script:

```python
import argparse
import sys

def build_parser():
    parser = argparse.ArgumentParser(prog="wordcount", description="Count lines and words.")
    parser.add_argument("filename")
    parser.add_argument("--words", action="store_true", help="count words, not lines")
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        with open(args.filename, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"wordcount: error: {e.strerror}: {args.filename}", file=sys.stderr)
        return 1
    count = len(text.split()) if args.words else len(text.splitlines())
    print(count)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Four ideas hold the design together:

1. **`build_parser()`** only builds the parser, so it can be tested.
2. **`main(argv=None)`** does the work and **returns an exit code**. With `argv=None` argparse reads the real command line; tests pass their own list.
3. **Errors the user can fix** (a missing file) are caught, shown as a short message on **stderr**, and turned into **exit code 1**. No traceback.
4. **`sys.exit(main())`** under `if __name__ == "__main__":` hands the code to the operating system. When the file is **imported** (by a test), nothing runs.

Run as a real program, the script gives exit code **0** for success, **1** for a runtime problem (file not found), and **2** for wrong usage (argparse). The messages go to stderr; stdout stays clean.

### 17.8 Testing a command-line tool

Save the script above as `wordcount.py`, next to a file `poem.txt` with two lines (6 words). Because `main(argv)` takes a list and returns a code, a test needs no real command line. It captures the output with `redirect_stdout` and `redirect_stderr` (section 16.4):

```python
import io
from contextlib import redirect_stdout, redirect_stderr
from wordcount import main

def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()

print(run(["poem.txt"]))
print(run(["ghost.txt"]))
code, out, err = run([])
print(code, repr(out), "usage:" in err)
```
```text
(0, '2\n', '')
(1, '', 'wordcount: error: No such file or directory: ghost.txt\n')
2 '' True
```

The helper `run` returns the exit code and both streams. The third call has no arguments, so argparse printed the usage on stderr and exited with 2, and we caught the `SystemExit`. Real test suites (pytest) use the same method. **That is the third outcome of this module: a command-line tool with arguments and helpful errors.**

### 17.9 Predict the output

**Predict the output.** Three `parse_args` calls on the same parser. What are the defaults?

```python
import argparse
parser = argparse.ArgumentParser(prog="t")
parser.add_argument("src")
parser.add_argument("dst", nargs="?", default="out")
parser.add_argument("-n", type=int, default=1)
parser.add_argument("-v", action="store_true")
parser.add_argument("--tag", action="append")
print(parser.parse_args(["a"]))
print(parser.parse_args(["a", "b", "-n", "5", "-v"]))
print(parser.parse_args(["--tag", "x", "a", "--tag", "y"]))
```
<details><summary>Answer</summary>

```text
Namespace(src='a', dst='out', n=1, v=False, tag=None)
Namespace(src='a', dst='b', n=5, v=True, tag=None)
Namespace(src='a', dst='out', n=1, v=False, tag=['x', 'y'])
```


The first call gives only `src`, so `dst` is its default `'out'`, `n` is 1, the flag `v` is `False`, and `tag` is `None` (no default was given). The second call gives all values; note that `-n 5` becomes the **integer** 5. In the third call, options come before and after the positional: argparse accepts options in any position, and `append` collects both values.
</details>

## 18. Project: a file organiser CLI

### 18.1 The goal

The downloads folder of most people is a mess: photos, PDFs, spreadsheets and scripts in one place. We build a tool, **`organise`**, that sorts the files of a folder into sub-folders by **type**, **date** or **size**. It uses the whole chapter: `pathlib` for paths, `shutil` for moving, `argparse` for the command line, error handling with exit codes, and a **`--dry-run`** option that shows what would happen without touching a single file. A tool that moves files must never surprise its user.

```text
organise SOURCE [--by {date,size,type}] [--dest DEST] [--copy] [-n | --dry-run] [-q]
```

Design rules:

1. **Separate thinking from doing.** One function computes a **plan** (a list of "move A to B") and does not touch the disk. Another **carries it out**. Then `--dry-run` is trivial: print the plan, do not carry it out. It is also easy to test.
2. **Never overwrite.** If the target name exists, choose a new name (`photo (1).jpg`).
3. **Look only at the files directly inside the source folder.** Skip folders and hidden files. Then a second run finds nothing to do.
4. **Helpful errors**: a clear message; exit code 2 for bad usage, 1 for a runtime problem.

### 18.2 Step by step

**Step 1, the rule "by type".** A dictionary maps a folder name to a set of suffixes; we compare **lower-case** suffixes. Unknown suffixes go to `other`. The table is data, so a new file type means a new line, not new logic.

```python
from pathlib import Path

TYPE_FOLDERS = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "documents": {".pdf", ".txt", ".md", ".docx", ".odt"},
    "data": {".csv", ".json", ".toml", ".xlsx"},
    "code": {".py", ".js", ".html", ".css"},
    "archives": {".zip", ".tar", ".gz"},
}

def folder_by_type(path):
    suffix = path.suffix.lower()
    for folder, suffixes in TYPE_FOLDERS.items():
        if suffix in suffixes:
            return folder
    return "other"

for name in ["Holiday.JPG", "cv.pdf", "run.py", "backup.tar.gz", "Makefile", "song.mp3"]:
    print(f"{name:14} -> {folder_by_type(Path(name))}")
```
```text
Holiday.JPG    -> images
cv.pdf         -> documents
run.py         -> code
backup.tar.gz  -> archives
Makefile       -> other
song.mp3       -> other
```

**Step 2, "by date" and "by size".** (`datetime` is covered fully in core.17; here we need only one call.) By date uses the modification time, in UTC so that the answer is the same in every country: `datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m")` gives names like `2026-03`. By size compares `st_size` with two named limits: below 10 KB is `small`, below 1 MB is `medium`, the rest is `large`.

**Step 3, never overwrite.** `unique_target(target)` returns the target if the name is free, and otherwise tries `name (1).ext`, `name (2).ext`, ... using `Path.with_name`, `stem` and `suffix`.

**Step 4, plan and carry out**, then **step 5, the parser and `main`**. Here is the complete tool. Read it from the top; each function does one job, and `main` joins them.

```python
"""organise.py - sort the files of a folder into sub-folders."""
import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

TYPE_FOLDERS = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "documents": {".pdf", ".txt", ".md", ".docx", ".odt"},
    "data": {".csv", ".json", ".toml", ".xlsx"},
    "code": {".py", ".js", ".html", ".css"},
    "archives": {".zip", ".tar", ".gz"},
}
SMALL = 10 * 1024          # below 10 KB: "small"
LARGE = 1024 * 1024        # 1 MB and more: "large"

def folder_by_type(path):
    suffix = path.suffix.lower()
    for folder, suffixes in TYPE_FOLDERS.items():
        if suffix in suffixes:
            return folder
    return "other"

def folder_by_date(path):
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return modified.strftime("%Y-%m")

def folder_by_size(path):
    size = path.stat().st_size
    if size < SMALL:
        return "small"
    if size < LARGE:
        return "medium"
    return "large"


RULES = {"type": folder_by_type, "date": folder_by_date, "size": folder_by_size}

def unique_target(target):
    """Return target, or 'name (1).ext', 'name (2).ext'... if it already exists."""
    if not target.exists():
        return target
    n = 1
    while True:
        candidate = target.with_name(f"{target.stem} ({n}){target.suffix}")
        if not candidate.exists():
            return candidate
        n += 1

def plan_moves(source, dest, by):
    """List (from, to) pairs. Touches nothing on disk."""
    rule = RULES[by]
    plan = []
    for path in sorted(source.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue                      # skip folders and hidden files
        plan.append((path, unique_target(dest / rule(path) / path.name)))
    return plan

def carry_out(plan, copy, dry_run, say):
    verb = "copy" if copy else "move"
    past = "copied" if copy else "moved"
    for source, target in plan:
        shown = f"{source.name} -> {target.parent.name}/{target.name}"
        if dry_run:
            say(f"would {verb} {shown}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if copy:
            shutil.copy2(source, target)
        else:
            shutil.move(source, target)
        say(f"{past} {shown}")

def existing_folder(text):
    path = Path(text)
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"{text!r} is not a folder")
    return path

def build_parser():
    parser = argparse.ArgumentParser(
        prog="organise",
        description="Sort the files of a folder into sub-folders.")
    parser.add_argument("source", type=existing_folder,
                        help="folder whose files should be sorted")
    parser.add_argument("--by", choices=sorted(RULES), default="type",
                        help="sort rule (default: %(default)s)")
    parser.add_argument("--dest", type=Path,
                        help="where the sub-folders go (default: inside SOURCE)")
    parser.add_argument("--copy", action="store_true",
                        help="copy the files instead of moving them")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="show what would happen, change nothing")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print nothing except errors")
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    dest = args.dest if args.dest is not None else args.source
    say = (lambda text: None) if args.quiet else print
    try:
        plan = plan_moves(args.source, dest, args.by)
        if not plan:
            say("nothing to do")
            return 0
        carry_out(plan, args.copy, args.dry_run, say)
    except OSError as e:
        print(f"organise: error: {e}", file=sys.stderr)
        return 1
    say(f"{len(plan)} file(s) handled" + (" (dry run, nothing changed)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Points to notice:

- `RULES` is a dict from the option text to a **function**, so `RULES[args.by]` picks the rule without an `if/elif` chain (functions are values). The parser's `choices=sorted(RULES)` comes from the same dict, so the two never disagree.
- `plan_moves` only **reads** the disk. `carry_out` is the only function that changes it, and it checks `dry_run` first.
- `existing_folder` is a **custom type**: a source that is not a folder becomes a usage error.
- `except OSError` in `main` turns any file problem (permission denied, disk full) into a one-line message and exit code 1.
- `say` is `print` or a function that does nothing, so `--quiet` needs no `if` elsewhere.
- No global state except constants, so `main(argv)` can be called many times in tests.

### 18.3 Trying it

We build an `inbox` folder with four visible files (known sizes and dates), a hidden file and a sub-folder. First a **dry run**, then the real run, then the tree, then a second run:

```python
import os
from pathlib import Path
from organise import main

def make(name, size, mtime):
    p = Path("inbox") / name
    p.parent.mkdir(exist_ok=True)
    p.write_bytes(b"x" * size)
    os.utime(p, (mtime, mtime))

JAN, MAR = 1_767_225_600, 1_772_323_200      # 2026-01-01 and 2026-03-01 (UTC)
make("holiday.JPG", 3_000, JAN)
make("cv.pdf", 20_000, MAR)
make("script.py", 800, JAN)
make("README", 50, JAN)
make(".hidden", 5, JAN)
Path("inbox/old").mkdir()

print("== dry run ==")
print("exit code", main(["inbox", "--dry-run"]))
print("== real run ==")
print("exit code", main(["inbox"]))
for p in sorted(Path("inbox").iterdir()):
    print("  ", p.name, sorted(c.name for c in p.iterdir()) if p.is_dir() else "")
print("== run again ==")
main(["inbox"])
```
```text
== dry run ==
would move README -> other/README
would move cv.pdf -> documents/cv.pdf
would move holiday.JPG -> images/holiday.JPG
would move script.py -> code/script.py
4 file(s) handled (dry run, nothing changed)
exit code 0
== real run ==
moved README -> other/README
moved cv.pdf -> documents/cv.pdf
moved holiday.JPG -> images/holiday.JPG
moved script.py -> code/script.py
4 file(s) handled
exit code 0
   .hidden 
   code ['script.py']
   documents ['cv.pdf']
   images ['holiday.JPG']
   old []
   other ['README']
== run again ==
nothing to do
```

The dry run prints the plan and changes nothing. The real run moves the four files into sub-folders created on demand. The hidden file and the folder `old` stay. The second run has nothing to do: the files are inside sub-folders now, and the tool only looks at the top level. Running it twice is **safe** (we say it is **idempotent**).

Now copying, another destination, and a name clash:

```python
import os
from pathlib import Path
from organise import main

for name, size, mtime in [("a.txt", 10, 1_767_225_600), ("b.txt", 20_000, 1_772_323_200)]:
    p = Path("src") / name
    p.parent.mkdir(exist_ok=True)
    p.write_bytes(b"x" * size)
    os.utime(p, (mtime, mtime))

print("== by date, copy, to another folder ==")
main(["src", "--by", "date", "--copy", "--dest", "sorted"])
print("== by size, quiet ==")
main(["src", "--by", "size", "--dest", "bysize", "-q"])
print(sorted(str(p) for p in Path("bysize").rglob("*.*")))
print("== name clash ==")
Path("src2").mkdir()
Path("src2/a.txt").write_text("new a")
os.utime("src2/a.txt", (1_767_225_600, 1_767_225_600))
main(["src2", "--by", "date", "--dest", "sorted"])
print(sorted(p.name for p in Path("sorted/2026-01").iterdir()))
```
```text
== by date, copy, to another folder ==
copied a.txt -> 2026-01/a.txt
copied b.txt -> 2026-03/b.txt
2 file(s) handled
== by size, quiet ==
['bysize/medium/b.txt', 'bysize/small/a.txt']
== name clash ==
moved a.txt -> 2026-01/a (1).txt
1 file(s) handled
['a (1).txt', 'a.txt']
```

- `--by date --copy --dest sorted` copied the files into `sorted/2026-01` and `sorted/2026-03`, and left the sources alone.
- `--by size -q` printed nothing and made `small` and `medium` folders (the `bysize` listing shows where each file went).
- A new `a.txt` met an existing `a.txt` in `sorted/2026-01`. It was stored as `a (1).txt`: nothing was overwritten.

### 18.4 Testing the tool

Each test uses a `TemporaryDirectory` (section 15), so nothing real is touched, and calls `main` with a list (section 17.8):

```python
import tempfile
from pathlib import Path
from organise import main

def test_dry_run_changes_nothing():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "a.jpg").write_text("x")
        assert main([d, "--dry-run", "-q"]) == 0
        assert (root / "a.jpg").exists()
        assert not (root / "images").exists()

def test_move_by_type():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "b.py").write_text("x")
        main([d, "-q"])
        assert (root / "code" / "b.py").exists()

for test in [test_dry_run_changes_nothing, test_move_by_type]:
    test()
    print("passed:", test.__name__)
```
```text
passed: test_dry_run_changes_nothing
passed: test_move_by_type
```

## 19. Common traps

Most of these appeared earlier; the section number tells you where.

1. **`"w"` erases at `open`** (2.2). Use `"a"` to add, `"x"` to protect, and the atomic recipe (8) to replace.
2. **No `encoding="utf-8"`** (4.5). The default differs between computers.
3. **`read()` or `readlines()` on a big file** (7.3). Loop over the file, or read chunks.
4. **Forgetting `with`** (5.1). Data stays in the buffer; a crash loses it.
5. **Strings from files and CSV** (11.2). Everything is text. Convert with `int()` and `float()`.
6. **CSV without `newline=""`** (11.5). Blank rows on Windows, broken multi-line values.
7. **`print(line)` with the line's `\n`** (3.2) gives double spacing. And a file read once is used up (3.1).
8. **Relative paths and the working directory** (1.4, 9.4). Build paths from `Path(__file__).resolve().parent`.
9. **`mkdir` without `parents=True, exist_ok=True`**, and `"w"` never creates folders (6.1, 9.5).
10. **Suffix case, and the order of `iterdir`/`glob`** (9.3, 9.6). `.JPG` is not `.jpg`; use `sorted(...)`.
11. **`glob` and hidden files; `**` without `recursive=True`** (10.3).
12. **`except OSError` before `except FileNotFoundError`** (6.3), and forgetting that decode errors are `ValueError`s (6.5).
13. **`shutil.rmtree` and `pickle.load`** (10.2, 14.3). One erases without asking; the other can run code.
14. **JSON loses tuples, integer keys, sets and dates** (12.2, 12.4); **`tomllib` needs `"rb"`** and cannot write (13.1).
15. **Tracebacks instead of messages, and exit code 0 on failure** (6.6, 17.7). Print a short message to stderr and return a non-zero code.

## 20. Summary

- A file is a **name** plus a row of **bytes**. `open(path, mode, encoding=...)` gives a file object. Modes: `"r"` read, `"w"` write (**erases at open**), `"a"` append, `"x"` create only, `"r+"` read and write; add `"b"` for bytes.
- **Text** is `str`, **binary** is `bytes`; the *encoding* converts between them. Always write `encoding="utf-8"`. `errors=` chooses what happens with bad bytes; `utf-8-sig` removes a BOM; `newline=` controls line endings (and must be `""` for CSV).
- Read with `for line in f` (lazy, one line at a time), `read()`, `readline()`, `readlines()`. A file is used up after one pass. Write with `write`, `writelines` (no newlines added), `print(file=f)`. Data is only safe after `close()` or `flush()`.
- **`with open(...) as f`** closes the file however the block ends. A **context manager** has an enter step and an exit step. `@contextmanager` builds one from a generator: `yield` inside `try`, cleanup in `finally`. `suppress(...)` ignores one error type.
- Errors are subclasses of **`OSError`**: `FileNotFoundError`, `PermissionError`, `IsADirectoryError`, `FileExistsError`. Catch the specific ones first. Prefer **try/except** (EAFP) to checking with `exists`. Decode errors are `ValueError`s.
- **Streaming**: loop over lines, or read chunks with `iter(lambda: f.read(n), b"")`; keep summaries, not data; generator pipelines (core.10) give constant memory for any file size.
- **Safe overwrite**: write a temp file in the **same folder**, `flush` and `os.fsync`, then `os.replace`. It is **atomic**, so a crash leaves the old file or the new file, never a mix. Clean the temp file on error.
- **`pathlib`**: `/` joins; `name`, `stem`, `suffix`, `parent`, `with_suffix`; `exists`, `mkdir(parents=True, exist_ok=True)`, `read_text`, `write_text`, `iterdir`, `glob`, `rglob`, `stat`, `rename`, `unlink`, `resolve`, `relative_to`. **`shutil`** copies, moves and archives (and `rmtree` deletes a whole tree: be careful). **`glob`** matches patterns (no hidden files, sort the result).
- **CSV**: use `csv.reader` / `DictReader` / `writer` / `DictWriter` with `newline=""`; values are strings. **JSON**: `dumps`/`loads`/`dump`/`load`; no tuples, sets or dates; `default=` for extra types; JSON Lines streams. **TOML**: `tomllib.load(f)` with `"rb"`, read only. **INI**: `configparser`, all values strings.
- **pickle** keeps any Python object but is Python-only, fragile, and **unsafe**: loading can run code. Never unpickle untrusted data; use JSON.
- **`tempfile`**: `TemporaryDirectory`, `NamedTemporaryFile`, `mkstemp`: unique names and automatic cleanup.
- **Standard streams**: `stdin` in, `stdout` for results, `stderr` for errors. Exit code 0 means success. `io.StringIO` and `redirect_stdout` capture output for tests.
- **`argparse`**: positional arguments, options, flags, `type=`, `choices=`, `nargs=`, `action="append"`/`"count"`, subcommands; it writes `--help` and usage errors (exit code 2). Write `main(argv=None)` that **returns an exit code**, and call `sys.exit(main())`.

When you can stream a big file in constant memory, replace a file so that a crash never corrupts it, and build a tool with `argparse` that reports problems as clear messages and exit codes, you have met the outcomes of this module. The problems that follow practise each part, ending with a tool of your own.

### What comes next

In **core.13, Modules, packages and environments**, you split programs into files of your own: `import` for your own code, packages with `__init__.py`, virtual environments and `pip`, and `if __name__ == "__main__"` explained in full. Your `organise.py` is already a module in disguise: that is why we could `import` its `main` in the tests. In **core.14** you meet classes, and with them the objects you used here without building: `Path`, file objects and `csv.reader`.

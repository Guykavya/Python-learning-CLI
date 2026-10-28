# Trace: write, append and read positions

Each `with` block opens `demo.txt` in a new mode. Remember what `"w"`, `"a"` and `"r"` do to old content, and that reading moves the position forward. Run it in an empty folder: it creates `demo.txt`.

```python
with open("demo.txt", "w") as f:
    f.write("one\n")
    f.write("two\n")

with open("demo.txt", "a") as f:
    f.write("three\n")

with open("demo.txt") as f:
    print(f.read().splitlines())

with open("demo.txt", "w") as f:
    f.write("four")

with open("demo.txt", "a") as f:
    print(f.write("!!"))

with open("demo.txt") as f:
    print(f.read(2))
    print(f.readline())
    print(f.readline())
    print(f.read() == "")
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`. A print of an empty string is an empty line. The program never stops with an error, so you never need to write a traceback.

# Fix the injection

Chapter section 7.1 (the safe way to run programs, and the injection shown with `echo`) and "Try it: fix the injection". `count_lines(filename)` asks a child Python process to count the lines of a file. It builds one command **string** and runs it with `shell=True`:

```python
COUNT = "import sys; print(sum(1 for _ in open(sys.argv[1], encoding='utf-8')))"

def count_lines(filename):
    command = '"' + sys.executable + '" -c "' + COUNT + '" ' + str(filename)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return int(result.stdout.split()[0])
```

It works for `notes.txt`. Now a file arrives called `x; echo HACKED`. The shell reads the `;` as "end of the first command", runs the child on a file called `x`, and then runs `echo HACKED` as a **second command**. Here it is a harmless `echo`; in real life it is whatever the person who named the file wanted (`rm -rf ~`). A space in a name (`my notes.txt`) or a quote (`it's.txt`) breaks it too.

## Your task

Fix `count_lines` in `solution.py` so the file name is always **one argument and never code**:

- pass a **list** of arguments: `[sys.executable, "-c", COUNT, str(filename)]`, and **no** `shell=True`;
- `check=True`, so a failing child (missing file) raises `subprocess.CalledProcessError` instead of returning garbage;
- `capture_output=True, text=True` and a `timeout` (10 seconds is plenty);
- return the count as an `int`.

Keep the name `count_lines` and the constant `COUNT`.

## Example

```python
count_lines(folder / "notes.txt")          # 3
count_lines(folder / "my notes.txt")       # 2   (today: crashes)
count_lines(folder / "x; echo HACKED")     # 2   (today: runs a second command)
count_lines(folder / "missing.txt")        # raises subprocess.CalledProcessError
```

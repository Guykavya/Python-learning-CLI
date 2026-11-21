## Approach

```python
def count_lines(filename):
    result = subprocess.run([sys.executable, "-c", COUNT, str(filename)],
                            capture_output=True, text=True, check=True, timeout=10)
    return int(result.stdout.strip())
```

With a list, `subprocess` starts the program directly; there is no shell, so there is nothing that could interpret `;`, quotes, spaces or `$(...)`. The file name `x; echo HACKED` is passed as one string and the child simply opens a file with that strange name. `check=True` turns "the child failed" into an exception at the place where it happened, and `timeout` makes sure a stuck child cannot freeze the caller (section 7.1's rules). Using `sys.executable` runs the same Python, with the same packages, on every operating system.

## Complexity

One child process per call; O(lines) inside the child.

## Another way

For this job you do not need a child process at all: `sum(1 for _ in open(filename, encoding="utf-8"))` in your own process is faster and has no injection surface. Run a program only when you need *that* program (`git`, `ffmpeg`, `pg_dump`); then the list form is the rule. If a tool really needs a shell feature (a pipeline), build it in Python with two `run` calls and `input=`, as section 7.2 suggests. And when a file name could start with `-`, put `"--"` before it if the tool supports it, so it is not read as an option.

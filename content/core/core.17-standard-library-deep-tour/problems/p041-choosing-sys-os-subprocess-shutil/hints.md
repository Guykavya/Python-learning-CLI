## Hint 1

For each task ask: "is this about the *Python interpreter*, about *one file or variable of the OS*,
about *many files at once*, or about *another program*?" That question alone picks `sys`, `os`,
`shutil` or `subprocess`.

## Hint 2

The names to look for: `sys.executable`, `sys.exit`, `sys.stderr`; `os.environ.get`;
`shutil.copytree`, `shutil.rmtree`, `shutil.which`; `subprocess.run` with `capture_output=True`,
`text=True`, `check=True`. For question 8 think about Windows, about a folder name with a space or a `;`,
and about what `os.system` gives back.

## Hint 3

A plan for your answer:

```
for each task:
    module.function(...)  -- one line of code
    why: what the obvious alternative gets wrong (missing, not portable, unsafe, cannot capture)
question 8: portability, injection / spaces, error handling and output
```

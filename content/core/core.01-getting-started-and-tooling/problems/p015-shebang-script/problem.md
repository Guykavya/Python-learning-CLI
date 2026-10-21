# A script that runs itself

Make `solution.py` runnable as `./solution.py`, and make it report how it was
run:

```
Running as: __main__
Script file: solution.py
```

Requirements:

1. The **first line** is exactly `#!/usr/bin/env python3`.
2. Line 1 of output uses the special name `__name__`.
3. Line 2 uses `__file__`, reduced to just the file name with
   `os.path.basename(...)`.

After writing it, try it in the terminal:

```bash
$ chmod +x solution.py
$ ./solution.py
Running as: __main__
Script file: solution.py
$ python3 solution.py
Running as: __main__
Script file: solution.py
```

The tests copy your file, `chmod` it, and run it directly with `./`.

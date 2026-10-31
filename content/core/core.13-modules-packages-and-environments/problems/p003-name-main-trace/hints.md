## Hint 1

Python sets `__name__` before it runs a file. The file you start with `python file.py` gets one special
name. What name does a file get when it is **imported**?

## Hint 2

The started file is `__main__`; an imported file gets its module name (`tools`, `app`). The `if` block
runs only in the started file. In the third command nothing is started from a file: `-c` runs the
string as `__main__`, and that string imports `app`. Which `if` blocks run then?

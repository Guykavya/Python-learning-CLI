# Which Python am I?

Write a script that reports the version of the Python that runs it:

```
Major: 3
Minor: 14
Full: 3.14.4
```

(Your numbers will match *your* interpreter.)

- `Major` and `Minor` come from `sys.version_info` (use `.major` and `.minor`).
- `Full` comes from `platform.python_version()`.

Do not type the numbers yourself; the tests run your script and compare with
the real interpreter.

**Example**

On Python 3.12.3 the output is:
```
Major: 3
Minor: 12
Full: 3.12.3
```

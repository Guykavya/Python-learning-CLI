## Hint 1

Which class do you create, and which method reads a file? What does that method do when the file does not exist? How do you get one option as an `int` with a fallback?

## Hint 2

```
cp = configparser.ConfigParser()
cp.read(path, encoding="utf-8")
return {s: dict(cp[s]) for s in cp.sections()}
...
return cp.getint(section, option, fallback=fallback)
```

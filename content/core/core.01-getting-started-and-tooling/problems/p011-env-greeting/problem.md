# Greeting from the environment

Programs often take settings from **environment variables** instead of asking
the user. Write a script that reads two of them:

- `LEARNER_NAME`, default `stranger` when it is not set,
- `LEARNER_LEVEL`, default `beginner` when it is not set,

and prints:

```
Hello, <name>!
Level: <level>
```

Use `os.environ.get(...)` with a default. The script must not call `input()`.

**Examples**

```bash
$ LEARNER_NAME=Asha LEARNER_LEVEL=expert python3 solution.py
Hello, Asha!
Level: expert
$ python3 solution.py
Hello, stranger!
Level: beginner
$ export LEARNER_NAME=Ravi
$ python3 solution.py
Hello, Ravi!
Level: beginner
```

# A Dockerfile linter

Chapter sections 5.2 (the Dockerfile), 5.3 (the cache), 5.5 (exec form versus shell form), 5.6 (good image habits) and "Try it: why is this Dockerfile slow?". Docker is never run by the tests in this course, so you will work on the **text** of a Dockerfile: write a small linter that finds the mistakes the chapter warns about. (The real-world tools are `hadolint` and the build itself; this checker is a teaching subset.)

## What to write

```python
def lint_dockerfile(text: str) -> list[tuple[int, str]]: ...
```

It returns a list of `(line_number, code)` pairs, **sorted** (by line, then code). Line numbers start at 1; a finding about the whole file uses line `0`. An instruction written over several lines with a trailing `\` is **one** instruction, reported at its **first** line. Blank lines and lines starting with `#` are ignored. Instruction names are case-insensitive.

The rules, exactly (these are the only rules):

| Code | When | Reported at |
|---|---|---|
| `unpinned-base` | a `FROM` whose image has **no tag** (`FROM python`) or the tag `latest`. A digest (`image@sha256:...`), `FROM scratch`, a reference to an earlier stage (`FROM build`) and an image containing `$` (a build argument) are fine. Flags such as `--platform=...` are skipped; `AS name` is ignored. | the `FROM` line |
| `shell-cmd` | a `CMD` or `ENTRYPOINT` whose argument does **not** start with `[` (shell form: `sh` becomes PID 1 and swallows `SIGTERM`) | that line |
| `copy-before-install` | a `COPY` or `ADD` that copies the whole build context (a source of `.` or `./`; `--from=...` copies are ignored) **before** the first `RUN` that contains `pip install`. If there is no such `RUN`, no finding. | the `COPY`/`ADD` line |
| `no-user` | no `USER` instruction in the **last stage** (the last `FROM` and what follows it), or the last `USER` there is `root` or `0` (also `root:...`, `0:...`) | line `0` |
| `secret-in-env` | an `ENV` or `ARG` that sets a name containing `SECRET`, `PASSWORD`, `PASSWD`, `TOKEN`, `API_KEY` or `PRIVATE_KEY`, or ending in `_KEY`, to a **non-empty literal** value (a value starting with `$` is a reference, and a missing or empty value is not a secret). `ENV A=1 B=2` sets two names; the old form `ENV NAME value` is also allowed. | that line |
| `apt-no-cleanup` | a `RUN` that contains `apt-get install` or `apt install` but not `rm -rf /var/lib/apt/lists` | that line |

## Example

```python
lint_dockerfile("FROM python\nCOPY . /srv\nRUN pip install -r requirements.txt\nCMD python app.py\n")
# [(0, 'no-user'), (1, 'unpinned-base'), (2, 'copy-before-install'), (4, 'shell-cmd')]

lint_dockerfile(CHAPTER_DOCKERFILE)    # the Dockerfile of chapter section 5.2
# []
```

The tests give you the chapter's final Dockerfile and expect `[]` for it. A correct but different Dockerfile is judged **only** by the six rules above.

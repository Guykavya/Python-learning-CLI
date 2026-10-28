# Explain: version ranges, pins and lock files

Two teams argue about dependencies.

Team A writes a **library**, `tinytables`, and its `pyproject.toml` says:

```toml
dependencies = ["requests>=2.28,<3"]
```

Team B writes a web **application** and deploys it to a server. Their app worked on Monday. On
Thursday they rebuilt the server from the same code, and it crashed: a package three levels deep
(a dependency of a dependency) had released a new version on Wednesday with a breaking change. Their
`requirements.txt` only said:

```text
flask
tinytables
```

Rohan from Team B says: "Fine, from now on we pin everything with `==` in `pyproject.toml`, also in
`tinytables`." Kavya thinks that is only half right.

In `answer.md` (about 200 to 350 words), explain:

1. What a **range** (`>=2.28,<3`) and a **pin** (`==2.31.0`) promise, and why each is useful.
2. Why the app broke on Thursday even though **its own code** and its `requirements.txt` did not change.
   Use the words *transitive dependency* and *resolver*.
3. Why a **library** like `tinytables` should declare ranges and not exact pins. What would happen
   to users who install `tinytables` together with another library that pins `requests==2.30.0`?
4. What a **lock file** is (`uv.lock`, `poetry.lock`, or a fully pinned `requirements.txt` from
   `pip freeze` / `pip-compile`), what it records (every package, including transitive ones, with exact
   versions, often with hashes), and why the app should have one.
5. How the two fit together: ranges in `pyproject.toml` say what *works*; the lock file says what
   was *tested*. How do you upgrade on purpose?

## Example of the level of detail

"`>=2.28,<3` means: any 2.x version from 2.28 on. The resolver picks the newest one that fits, so
the version you get depends on the day you install." A good answer goes on like this for each point.

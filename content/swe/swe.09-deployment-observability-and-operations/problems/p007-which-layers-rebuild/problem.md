# Which layers rebuild?

Chapter section 5.3 (build it, and understand the cache) and "Try it: why is this Dockerfile slow?". Docker builds an image **step by step**, one step per instruction, and remembers each result. A step is reused from the cache only if **all the steps before it were reused**, its own text is unchanged and, for `COPY`, the copied files are unchanged. The first step that misses the cache makes **every step after it** miss too.

The program models this for the Dockerfile of the chapter (plus `USER` and `CMD`, which are steps too). It runs a first build, then five separate edits, **each one started from the cache of the first build**. (It does not run Docker: the real build log of the chapter, section 5.3, shows exactly this pattern for the steps it lists.)

```python
import hashlib

DOCKERFILE = [
    "FROM python:3.14-slim",
    "RUN useradd --create-home app",
    "WORKDIR /srv",
    "COPY requirements.txt .",
    "RUN pip install -r requirements.txt",
    "COPY app ./app",
    "RUN mkdir /data && chown app:app /data",
    "USER app",
    'CMD ["uvicorn", "app.main:create_app", "--factory"]',
]
FILES = {"requirements.txt": "fastapi==0.1", "app/main.py": "print('v1')", "README.md": "docs"}


def build(dockerfile, files, cache):
    """Run every step. A step is a cache hit only if the key of the step before it was a hit
    and the step's own text (and, for COPY, the copied files) are unchanged. Returns the steps that missed."""
    missed, chain = [], ""
    for number, line in enumerate(dockerfile, start=1):
        key = chain + "|" + line
        if line.startswith("COPY "):
            source = line.split()[1]
            copied = sorted((name, text) for name, text in files.items() if name == source or name.startswith(source + "/"))
            key += "|" + repr(copied)
        key = hashlib.sha256(key.encode()).hexdigest()
        if key not in cache:
            missed.append(number)
            cache.add(key)
        chain = key
    return missed


def with_line(dockerfile, number, text):
    changed = list(dockerfile)
    changed[number - 1] = text
    return changed


cache = set()
build(DOCKERFILE, FILES, cache)                       # the first build fills the cache
trials = [
    ("app/main.py edited", DOCKERFILE, {**FILES, "app/main.py": "print('v2')"}),
    ("requirements.txt edited", DOCKERFILE, {**FILES, "requirements.txt": "fastapi==0.2"}),
    ("base image tag changed", with_line(DOCKERFILE, 1, "FROM python:3.13-slim"), FILES),
    ("CMD line edited", with_line(DOCKERFILE, 9, 'CMD ["uvicorn", "app.main:create_app"]'), FILES),
    ("README.md edited", DOCKERFILE, {**FILES, "README.md": "more docs"}),
]
for label, dockerfile, files in trials:
    missed = build(dockerfile, files, set(cache))     # every trial starts from the same cache
    if missed:
        print(f"{label}: first miss at step {missed[0]}, steps rebuilt: {len(missed)}")
    else:
        print(f"{label}: every step is cached")
```

## What to write

The exact output: five lines.

## Example

If you only changed the text of step 9 (the last one), the first miss is step 9 and 1 step is rebuilt: `first miss at step 9, steps rebuilt: 1`.

## After you answer

- In which order would you have to write the Dockerfile so that editing `app/main.py` rebuilt **only** the last steps? Is the given order already best?
- Why is a change to `README.md` free, while the same change would cost a full rebuild if the Dockerfile said `COPY . .` as step 4? (`.dockerignore` can also fix that.)

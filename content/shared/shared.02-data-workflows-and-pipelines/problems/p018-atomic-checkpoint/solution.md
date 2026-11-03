## Approach

**Saving.** Walk through every crash point:

| Crash during | `cp.json` afterwards |
|---|---|
| `json.dumps` (or a `TypeError`) | old checkpoint, untouched |
| writing `cp.json.tmp` | old checkpoint; a broken `.tmp` that nobody reads |
| `os.replace` itself | the OS guarantees: old file **or** new file |
| after `os.replace` | new checkpoint |

There is no row with a half-written `cp.json`. That is what "atomic" means. `flush()` +
`os.fsync()` push the bytes to the disk before the rename, so after a power cut the renamed
file is not empty (without them the rename can reach the disk before the data does).

**Loading.** A loader that crashes on a bad checkpoint makes the pipeline un-runnable until a
human deletes a file at 3 a.m. A loader that silently ignores it hides a real problem. The
middle way: keep the evidence (`.corrupt`), say so loudly (a `WARNING`), and continue from the
default, which means "start from the beginning". That is safe **only because** the loads are
idempotent (upserts): re-doing work duplicates nothing.

Returning `dict(default)` instead of `default` matters: the caller usually mutates the state
(`state["loaded"] += 3`) and would otherwise change its own default constant.

## Code

```python
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("pipeline")


def save_checkpoint(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(state, ensure_ascii=False, indent=2)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_checkpoint(path, default=None):
    path = Path(path)
    fallback = dict(default) if default is not None else {}
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return fallback
    except UnicodeDecodeError:
        text = None
    try:
        state = json.loads(text) if text is not None else None
    except ValueError:
        state = None
    if isinstance(state, dict):
        return state
    corrupt = path.with_name(path.name + ".corrupt")
    os.replace(path, corrupt)
    logger.warning("checkpoint %s is corrupt; moved to %s, starting from the default", path, corrupt.name)
    return fallback
```

## Complexity

O(s) time and memory for a state of size s. Checkpoints should stay small (a cursor, a few
counters); the data itself belongs in the database or data files.

## Another way

`tempfile.NamedTemporaryFile(dir=path.parent, delete=False)` gives a unique temp name, which
matters if two processes might save at the same moment; you then remove the temp file in an
`except` block if anything fails. Some pipelines also keep the previous checkpoint as
`cp.json.bak` and fall back to it when `cp.json` is corrupt. Another option is to keep the
checkpoint in the same SQLite database as the data, so a single transaction updates both
(p015's state table); then there is no file to corrupt at all.

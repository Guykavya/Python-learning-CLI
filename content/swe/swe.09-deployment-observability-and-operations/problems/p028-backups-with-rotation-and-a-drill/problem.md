# Backups with rotation and a drill

Chapter sections 13.1 (the only backup that counts is one you have restored), 13.2 (tutorial: SQLite backup, disaster and restore) and 13.4 (make it routine), and "Try it: what did the drill not test?". **Copying a SQLite file while the application is writing can produce a corrupt copy.** SQLite's own **online backup API** (`sqlite3.Connection.backup`) takes a consistent snapshot. Write the backup function with rotation, and the **restore drill** that proves a backup can be used.

## What to write

```python
def backup(db_file, backup_dir, keep=7, now=time.time) -> tuple[Path, str]: ...
def drill(backup_file, min_orders=1) -> tuple[list[tuple[str, bool]], int]: ...
```

**`backup(db_file, backup_dir, keep=7, now=time.time)`**

1. `keep` must be at least 1, else `ValueError`. Create `backup_dir` if needed.
2. The target is `backup_dir / f"{stem}-{stamp}.db"` where `stem` is the database file's name without its extension and `stamp` is `now()` formatted as UTC `YYYYmmddTHHMMSSZ` (`time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now()))`). `now` is injected so the tests control the names.
3. Open the source **read-only** (`sqlite3.connect(db_file_uri + "?mode=ro", uri=True)`, with `Path(db_file).resolve().as_uri()` for the URI), open the target, and copy with `source.backup(target)`. Run `PRAGMA integrity_check` on the **copy**. Close both connections (`contextlib.closing`) before anything else is done to the files.
4. If anything about the database fails (`sqlite3.DatabaseError`, which includes a missing or non-database source) or the integrity check does not say `ok`, **delete the target** (never keep a backup you know is bad) and raise `RuntimeError` whose message starts with `backup FAILED`.
5. Write the checksum file `<target>.sha256` containing `f"{digest}  {target.name}\n"` where `digest` is the SHA-256 hex digest of the backup file.
6. **Rotation:** among the files `backup_dir/f"{stem}-*.db"`, sorted by name, keep the newest `keep` and delete the others **with their `.sha256` files**. Other databases' backups (other stems) are never touched.
7. Return `(target_path, digest)`.

**`drill(backup_file, min_orders=1)`** restores a backup into a temporary folder and returns `(steps, count)`:

- `steps` is a list of **four** `(name, ok)` pairs, in this order and with these names:
  `"checksum matches"` (the file's SHA-256 equals the first word of `<backup_file>.sha256`; a missing or empty checksum file is `False`, not an exception), `"integrity check ok"`, `"table 'orders' exists"`, `f"at least {min_orders} order(s) present"`.
- Restore with `source.backup(target)` into `tempfile.TemporaryDirectory()` (open the backup read-only too), then run the checks on the restored copy. If the backup is not a readable database (`sqlite3.DatabaseError`), the last three steps are `False` and `count` is `0`.
- `count` is `SELECT count(*) FROM orders` of the restored copy (`0` if there is no such table).
- If `backup_file` does not exist, raise `FileNotFoundError`.

## Example

```python
path, digest = backup("pagebound.db", "backups", keep=3, now=lambda: 1_700_000_000)
path.name                       # 'pagebound-20231114T221320Z.db'
drill(path, min_orders=20)
# ([('checksum matches', True), ('integrity check ok', True), ("table 'orders' exists", True), ('at least 20 order(s) present', True)], 120)
```

What the drill does **not** test (chapter "Try it"): that the **application** works with the restored database (version, migrations, file ownership), and everything outside the database (uploads, secrets, configuration, DNS). A full drill rebuilds the whole service from backups on clean infrastructure.

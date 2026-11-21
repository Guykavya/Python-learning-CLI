## Hint 1

Why not `shutil.copy`? What could the application be doing to the file while you copy it? Which `sqlite3` method gives you a consistent snapshot? Then for the drill: a backup is only worth something if you can **read the data back** from a place where nothing else helps you. What four questions does the chapter's drill ask?

## Hint 2

```text
backup: stamp -> target name; open source read-only (URI mode=ro) and target; source.backup(target); PRAGMA integrity_check on the copy
        error or not "ok" -> delete the target, raise RuntimeError("backup FAILED: ...")
        write <target>.sha256 = "<digest>  <name>\n"; rotation: sorted(glob(stem-*.db))[:-keep] -> delete with their .sha256
drill:  checksum from the sidecar (missing -> False); restore with source.backup into a temp folder;
        integrity_check, table 'orders' in sqlite_master, count(*) from orders; DatabaseError -> the last three steps False
```
Close every connection (`contextlib.closing`) before deleting or reading the files again: Windows cannot delete an open file.

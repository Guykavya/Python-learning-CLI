## Hint 1

Build the small, pure pieces first: `backup_name` / `parse_backup_name` (only `datetime`), then
`sha256_file`, `build_manifest`, `manifest_text`, `parse_manifest`. Each is a few lines and fully
tested on its own. Questions to settle: how do you turn an aware datetime into UTC? How do you parse
`"20250115-093000"` back, and what does `strptime` raise for month 13? How do you split
`"<digest>  my file.txt"` into exactly two parts?

## Hint 2

- `when.astimezone(timezone.utc).strftime("%Y%m%d-%H%M%S")`; `datetime.strptime(stamp, STAMP).replace(tzinfo=timezone.utc)`.
- `create_backup`: check `src.is_dir()`; compare `src.resolve()` with `dest_dir.resolve()` and its `.parents`;
  write to `final.with_name(final.name + ".part")` inside `try`, then `os.replace(part, final)`;
  in `except BaseException:` unlink the part file and re-raise.
- `verify_backup`: `names = set(zf.namelist())`; `expected = parse_manifest(zf.read(MANIFEST).decode("utf-8"))`;
  compare digests computed from `zf.open(name)`.
- `list_backups`: `(parse_backup_name(prefix, p.name), p)` pairs for names that parse, sorted.
- `rotate_backups`: check `keep >= 1` **first** (`backups[:-0]` is an empty list, not "all of them").
- `setup_log`: remove and close the old handlers, then add one `RotatingFileHandler`.

## Hint 3

```
create_backup(src, dest_dir, prefix, clock, logger):
    defaults for clock and logger
    if not src.is_dir(): FileNotFoundError
    if dest is src or inside src: ValueError
    manifest = build_manifest(src);  if MANIFEST in manifest: ValueError
    mkdir dest_dir; final = dest_dir / backup_name(prefix, clock()); if final.exists(): FileExistsError
    part = final + ".part"
    try:
        with ZipFile(part, "w", ZIP_DEFLATED) as zf:
            for name in manifest: zf.write(src / name, arcname=name)
            zf.writestr(MANIFEST, manifest_text(manifest))
        os.replace(part, final)
    except BaseException: part.unlink(missing_ok=True); raise
    logger.info("created %s (%d files, %d bytes)", final.name, len(manifest), final.stat().st_size)
    return final

run_backup(...):
    created = create_backup(...)
    problems = verify_backup(created)
    if problems: logger.error(...); raise RuntimeError
    deleted = rotate_backups(dest_dir, prefix, keep, logger)
    return {"created": created, "deleted": deleted, "files": number of members except MANIFEST}
```

- Calling `pq.write_to_dataset` with the default behaviour on a re-run. It adds a new uniquely named
  file beside the old one, so the day holds both versions and every total doubles.
- Deleting the whole dataset (`shutil.rmtree(root)`) to "start clean". Every other day is lost.
- Deleting the day's folder first and building the table afterwards. One bad value and the day
  has no data at all, with nothing left to fall back to.
- Writing the new file straight into the existing folder next to the old one and deleting the old
  file afterwards: a crash in between leaves both files, and readers see duplicates.
- Leaving the temporary folder behind on success. It is ignored by pyarrow because of the leading
  `.`, but it wastes space and confuses the next run.
- `os.replace(tmp, folder)` while `folder` still exists. On Windows (and for non-empty folders on
  Linux) this fails; move the old folder away first.
- Not checking that every row belongs to the day. A misplaced row is counted on the wrong day, and
  the next overwrite of its real day will not remove it.

- Appending the folder to the **end** of `sys.path`. It works here, but a module with the same name earlier
  on the path (even in the standard library) would win. Front means "my files first".
- Inserting the folder on every call. `sys.path` grows with duplicates.
- Forgetting `importlib.invalidate_caches()`. A file written after the folder was first searched may be
  "not found" even though it is on disk.
- Calling `import_module` a second time and expecting new code. The module is cached in `sys.modules`;
  only `reload` runs the file again.
- Using `exec(open(file).read())`. That runs the code, but it does not create a module object or cache it.

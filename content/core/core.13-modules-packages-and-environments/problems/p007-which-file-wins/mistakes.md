- Looping over the two kinds first (all packages, then all modules). A `name.py` in an earlier folder
  must beat a package in a later folder.
- Checking only that the folder `name/` exists. Without `__init__.py` it is not a regular package.
- Returning `True`/`False` or a string. The task asks for the `Path` of the file.
- Crashing on a missing folder with `os.listdir`. `is_file()` simply returns `False`.

- `sys.executable()`: it is a string, not a function, so calling it raises
  `TypeError: 'str' object is not callable`.
- `platform.system` without brackets prints `<function system at 0x...>`.
- Using the folder of the script (`__file__`) instead of the current working
  directory. They are different when you run `python3 code/solution.py` from
  another folder.

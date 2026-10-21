- Printing `mode & 4`, which shows `4` or `0`, not `True` or `False`.
- Writing `mode & 4 != 0` without brackets: `!=` binds tighter, so it is `mode & (4 != 0)`, which is `mode & True`.
  It happens to print 1 or 0 here, not a bool.
- Using `-` and `+` to clear and set bits, which breaks when the bit is already in that state.

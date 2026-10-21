- Writing `a = b` then `b = a`. After the first line both names refer to the same object,
  so the original value of `a` is gone and both print the second number.
- Using a third name like `temp`. It works, but this problem asks you to learn tuple assignment.
- Thinking `a, b = b, a` rebinds `a` before reading `a` on the right. The right side is fully evaluated first.

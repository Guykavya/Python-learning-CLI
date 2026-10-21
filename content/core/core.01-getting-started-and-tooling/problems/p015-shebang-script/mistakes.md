- Putting the shebang on line 2 (after a comment or a blank line). The kernel
  only looks at the first two bytes of the file.
- A space or typo: `# !/usr/bin/env python3` or `#!/usr/bin/env python 3`.
- Forgetting `chmod +x`: bash says `Permission denied`.
- Typing `solution.py` without `./`: bash says `command not found`, because the
  current folder is not in `PATH`.
- Printing `__file__` directly: it may show a full path such as
  `/home/asha/my-work/.../solution.py`.

- Wrong order of mock arguments with stacked decorators: the decorator closest to the function is the
  first argument. A swapped pair gives confusing "Mock has no attribute" errors.
- Forgetting `return_value=True`: a bare `patch` returns a `Mock`, which is truthy, so the "missing
  file" test passes for the wrong reason or the happy path hides a bug.
- Not asserting that `copy` was **not** called for the missing file.
- Using a real path (`/tmp/x.txt`) "because it is patched anyway": if a patch is wrong the test
  touches the real disk.
- Patching `shutil.copy` after `from shutil import copy` in the target: the target keeps its own
  name, so patch `target.copy`. Patch the name where it is looked up.

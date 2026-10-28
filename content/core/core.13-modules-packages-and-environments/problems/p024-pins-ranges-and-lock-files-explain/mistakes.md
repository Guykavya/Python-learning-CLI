- Saying "pin everything with `==` in `pyproject.toml`" for a library. Users then cannot combine it
  with other libraries, and they never get bug or security fixes.
- Thinking `requirements.txt` with only top-level names is a lock file. It pins nothing, and it says
  nothing about transitive dependencies.
- Forgetting transitive dependencies. Most breakage comes from packages you never listed.
- Thinking a lock file means you never upgrade. You upgrade on purpose: re-lock, test, commit.
- Mixing up "the code changed" and "the environment changed". Same code + different packages =
  different program.

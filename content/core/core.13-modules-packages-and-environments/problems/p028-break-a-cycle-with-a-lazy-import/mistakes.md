- Moving the import to the **bottom** of `audit.py`. It still runs at load time, before `accounts`
  defines `balance`, so it fails the same way.
- Swapping the order of the lines in `__init__.py`. `audit` loads first, then imports `accounts`,
  which imports `log` from the half-built `audit`: the same error in the other direction.
- Copying `balance` into `audit.py`. That is a second function; it may read a different dict and
  drift apart.
- Merging the two modules into one. It "works" but throws away the structure; the task says not to.
- Using `import accounts` (absolute, without the package) inside the function. There is no top-level
  module called `accounts`: use `from .accounts import balance` or `from bank.accounts import balance`.

## Hint 1

Which lines run while the file is open, and which run after the `with` block has ended? Does the `with` block still close the file when an error is raised inside it?

## Hint 2

The name `g` still exists after the block, but it points to a closed file. The same is true for `h`: the `with` statement closes the file before the `except` clause runs. A closed file still remembers its `name`.

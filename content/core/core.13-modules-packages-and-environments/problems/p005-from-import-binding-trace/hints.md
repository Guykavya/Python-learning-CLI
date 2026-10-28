## Hint 1

Draw two boxes: the namespace of `main` and the namespace of `settings`. After the first line, both have
a name `level` pointing to `1`. Which box does `bump()` change? (Its `global` means the module where
`bump` was **defined**.) Which box does `level = 99` change?

## Hint 2

Rebinding a name in one box never moves the name in the other box. But `names.append` does not rebind:
it changes the **list object**, which both names point to. `settings.names = ["cat"]` rebinds only the
`settings` name. A second `from settings import level` copies the current value of `settings.level` again.

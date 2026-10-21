## Hint 1

Imagine two projects needing two different versions of the same library. Where
would each version be installed without venvs?

## Hint 2

Run `ls .venv`, `cat .venv/pyvenv.cfg` and `ls -l .venv/bin/python` in a real
venv. Then compare `echo $PATH` before and after activating.

## Hint 3

For question 6, the core idea is "two different Pythons". Which commands print
the path of the Python that runs, and the path pip installs to?

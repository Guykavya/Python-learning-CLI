## Hint 1

Draw who needs whom. `words` needs `normalise` and `STOP_WORDS`. `count_words` needs `words`.
`report` needs `words` and `top_words`. If arrows only point "down" (reporting -> stats -> clean), can
there be a circular import? Which single line of the old script must never run on import?

## Hint 2

```text
clean.py      STOP_WORDS, normalise, words           (imports nothing from the package)
stats.py      from collections import Counter
              from .clean import words
              count_words, top_words
reporting.py  from .clean import words
              from .stats import top_words
              report
__init__.py   from .reporting import report
              from .stats import count_words, top_words
              __all__ = [...]; __version__ = "0.1.0"
__main__.py   import sys; from .reporting import report
              def main(): read argv and stdin, print
              if __name__ == "__main__": main()
```

Inside a triple-quoted string in `solution.py`, the `"\n".join` of `report` must be written as
`"\\n".join`, or use a raw string, so that the file gets a backslash-n and not a real line break.

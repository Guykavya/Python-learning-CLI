## Approach

The script starts as module `__main__` and prints `loading counter as __main__`. Inside the `if`
block it imports `helper`. `helper` imports `counter`. The cache has only `"__main__"`, not
`"counter"`, so Python runs `counter.py` a **second time** as a new module named `counter`. That run
prints `loading counter as counter`, and its `if` block is skipped. Then `helper` prints
`loading helper`.

Now there are two `hits` lists. `hit("main")` in the script uses the `__main__` list, so it returns 1.
`helper.go()` calls `counter.hit`, which uses the other list: 1, then 2. `import counter` in the script
finds the cached `counter` module, which is not the `__main__` module.

## Output

```text
loading counter as __main__
loading counter as counter
loading helper
main sees 1
helper sees 1
helper sees 2
same module? False
main hits: ['main']
counter hits: ['helper', 'helper']
```

## Complexity

Not applicable.

## Another way

The real fix is to never import your entry script. Keep the shared state in its own module
(`counter.py` with only `hits` and `hit`), and put the script part in a separate `main.py` that
imports `counter`. Then there is only one module object and one list.

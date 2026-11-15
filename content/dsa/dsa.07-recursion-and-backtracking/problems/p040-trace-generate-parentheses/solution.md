## Approach

Draw the tree for `n = 2`. Each node prints before deciding. The `(` child is explored completely before the `)` child.

## Expected output

```text
'' 0 0
'(' 1 0
'((' 2 0
'(()' 2 1
'(())' 2 2
'()' 1 1
'()(' 2 1
'()()' 2 2
['(())', '()()']
((()))
(()())
(())()
()(())
()()()
```

## Why

```text
'' 0 0
└── '(' 1 0
    ├── '((' 2 0 ── '(()' 2 1 ── '(())' 2 2   record
    └── '()' 1 1 ── '()(' 2 1 ── '()()' 2 2    record
```

8 calls instead of the `1 + 2 + 4 + 8 + 16 = 31` nodes of a tree with no pruning (16 strings of length 4). `)` cannot come first because `closed < opened` is `0 < 0`, false. Since `(` is always tried before `)`, the results appear in dictionary order: `((()))`, `(()())`, `(())()`, `()(())`, `()()()` (5, a Catalan number).

## Walkthrough

1. `,\s*` matches `", "` and `","`: pieces `a`, `b`, `c`.
2. Same matches, but `(,)` captures only the comma. It is inserted; the spaces are not:
   `['a', ',', 'b', ',', 'c']`.
3. Now the group is `(,\s*)`, so the first separator is kept **with** its space: `', '`.
4. `\d` matches `1`, `2`, `2` one digit at a time. Between the two `2`s there is nothing: an
   empty piece. `['x', 'y', '', 'z']`.
5. `(\d+)` matches `1` and `22` as whole runs and keeps them: `['x', '1', 'y', '22', 'z']`.
6. Two groups. At `-`: group 1 is `'-'`, group 2 did not take part → `None`. At `+`: `None`
   then `'+'`. Result: `['1', '-', None, '2', None, '+', '3']`.
7. Leading and trailing whitespace are separators too, so the first and last pieces are empty.
   (`"  lead and trail  ".split()` with no argument would drop them; `re.split` does not.)
8. `maxsplit=2`: two cuts, the rest `c,d` stays together.
9. One cut at the first `=`, and the group keeps it: `['key', '=', 'val=more']`.
10. Separators `;`, `;`, `,`: pieces `a`, `""` (between the two `;`), `b`, `""` (after the
    final `,`).
11. `parts` is `['2', '+', '3', '*', '4']`. Even positions are the numbers, odd positions the
    operators.

## The exact output

```text
['a', 'b', 'c']
['a', ',', 'b', ',', 'c']
['a', ', ', 'b', ',', 'c']
['x', 'y', '', 'z']
['x', '1', 'y', '22', 'z']
['1', '-', None, '2', None, '+', '3']
['', 'lead', 'and', 'trail', '']
['a', 'b', 'c,d']
['key', '=', 'val=more']
['a', '', 'b', '']
['2', '3', '4'] ['+', '*']
```

**Lesson:** a capturing group in a `split` pattern changes the result. Use `(?:...)` when you
need grouping but not the separators, and a capturing group on purpose when you do want them
(a tokenizer for `2+3*4`).

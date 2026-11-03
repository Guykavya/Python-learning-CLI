## Hint 1

Which rows does each join type keep: only matches, all left rows, or all rows from both sides? Which of the four SKUs (A1, B2, C3, D4) is present in only one list? For the emulation, think of two pieces: "everything on the left" and "what the left piece missed".

## Hint 2

```
inner : matches only                      -> B2, C3
left  : all stock + matches               -> A1, B2, C3
full  : all stock + all listing           -> A1, B2, C3, D4
emulation = LEFT JOIN rows (stock side)
            UNION ALL
            listing rows WHERE no stock row exists (LEFT JOIN ... WHERE s.sku IS NULL)
```

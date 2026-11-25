## Hint 1

What exactly is a *loss*? A value that had **content** in the raw text (not missing, not just spaces) but is missing after the conversion. Write the two boolean masks, "raw has content" and "clean is missing", and combine them with `&`. Which `.str` method tells you a text is only spaces?

## Hint 2

```text
for col in columns present in both frames (raw order):
    text      = raw[col] as "string"
    non_empty = text is not missing AND text.str.strip() != ""      # fillna(False) for the missing ones
    lost      = non_empty AND clean[col].isna()
    entry     = {"lost": int(lost.sum()),
                 "examples": text[lost].drop_duplicates().head(3).tolist()}
```
`drop_duplicates` keeps the first appearance, so the examples come out in order of appearance.

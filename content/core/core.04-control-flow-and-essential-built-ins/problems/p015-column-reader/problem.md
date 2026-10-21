# Read a message by columns

An old trick for hiding a message: write it in rows of a fixed **width**, then read it
**column by column**.

With the message `WEAREDISCOVERED` and width 5, the rows are:

```
WEARE
DISCO
VERED
```

Reading down each column, left to right, gives `WDV`, `EIE`, `ASR`, `RCE`, `EOD`, so the
output is `WDVEIEASRRCEEOD`.

Read the message (one line, spaces count as characters) and the width (a whole number).
Print the column-by-column text. The last row may be shorter than the others.

If the width is 0 or less, print `invalid width`.

**Examples**

| Message | Width | Output |
|---|---|---|
| `WEAREDISCOVERED` | `5` | `WDVEIEASRRCEEOD` |
| `abcdefg` | `3` | `adgbecf` |
| `hi` | `10` | `hi` |

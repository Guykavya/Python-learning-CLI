# Parse clock times

Read lines until a line `end`. Each line is a time in one of these forms:

- `H:MM` or `H:MM:SS` in 24-hour form, with the hour from 0 to 23
- the same followed by a space and `am` or `pm` (any capitals), with the hour from 1 to 12

The hour has 1 or 2 digits. Minutes and seconds have exactly 2 digits each, from 00 to 59.
Seconds default to 0.

For a valid time print `HH:MM:SS = N s`, where `HH:MM:SS` is the 24-hour time with two digits
each and `N` is the number of seconds since midnight. In 12-hour form, `12 am` is hour 0,
`12 pm` is hour 12, and other `pm` hours add 12.

For anything else print `invalid: <the line, stripped>`.

**Examples**

| Input | Output |
|---|---|
| `9:05` | `09:05:00 = 32700 s` |
| `23:59:59` | `23:59:59 = 86399 s` |
| `12:30 am` | `00:30:00 = 1800 s` |
| `7:15:30 PM` | `19:15:30 = 69330 s` |
| `24:00` | `invalid: 24:00` |
| `13:00 pm` | `invalid: 13:00 pm` |
| `9:5` | `invalid: 9:5` |

**Rule for this problem:** use `match` with sequence patterns to recognise the shapes.

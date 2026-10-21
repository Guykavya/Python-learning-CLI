# Read a fixed-width record

Old banking and government systems store records in **fixed-width** format: every field occupies the same columns on every line, padded with spaces or zeros. Read one record and print its fields.

| Columns (0-based, end excluded) | Field | Stored as |
|---|---|---|
| 0 to 6 | account id | digits, zero-padded |
| 6 to 26 | name | text, padded with spaces on the right |
| 26 to 36 | city | text, padded with spaces on the right |
| 36 to 46 | amount in paise | digits, zero-padded |

Print:

```
ID: <id as a number, no leading zeros>
Name: <name without padding>
City: <city without padding>
Amount: Rs <rupees with thousands separators>.<two-digit paise>
```

**Example**

Input (46 characters):
```
000042Asha Kumar          Pune      0000123456
```
Output:
```
ID: 42
Name: Asha Kumar
City: Pune
Amount: Rs 1,234.56
```

Do the money with whole numbers (`//` and `%` by 100), not floats.

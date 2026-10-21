# Password checks with any and all

Read a password (the whole line, without stripping). Print four checks and a verdict:

```
Length 8+: yes
Has digit: yes
Has capital: no
Only letters and digits: yes
Weak
```

- `Has digit`: at least one character is a digit.
- `Has capital`: at least one character is a capital letter.
- `Only letters and digits`: every character is a letter or a digit. For an **empty**
  password this says `yes`: there is no character that breaks the rule.
- The verdict is `Strong` if all four checks say `yes`, otherwise `Weak`.

Use `any()` for the "has" checks and `all()` for the "only" check. The tests check this.

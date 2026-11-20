# A modern password policy

Chapter section 2.4 (password policy: what current guidance says). Old rules ("one capital, one digit, one symbol") made people choose `Password1!`. Current guidance asks for **length**, allows **passphrases**, rejects **known-bad** passwords and does **not** force character types. Write the check.

```python
def check_password_policy(password: str, username: str = "", breached=frozenset()) -> list[str]: ...
```

Return a list of **problem codes**, in this order, for every rule that fails (an empty list means the password is accepted):

| Code | When |
|---|---|
| `"too_short"` | fewer than **12** characters |
| `"too_long"` | more than **256** characters (so nobody makes your server hash a 100 MB "password") |
| `"breached"` | the password, in lower case, is in the set `breached` (the set holds lower-case passwords) |
| `"contains_username"` | `username` is not empty and appears inside the password, ignoring case |
| `"one_character"` | the password is made of one single character repeated (`"aaaaaaaaaaaa"`) |

There are **no** rules about capitals, digits or symbols, and spaces are allowed. Length counts characters, not bytes.

## Example

```text
BAD = {"password1234", "qwertyuiop12"}
check_password_policy("short")                                   -> ["too_short"]
check_password_policy("Password1234", breached=BAD)              -> ["breached"]
check_password_policy("ada-lovelace-rules", "ada")               -> ["contains_username"]
check_password_policy("aaaaaaaaaaaa")                            -> ["one_character"]
check_password_policy("aaa")                                     -> ["too_short", "one_character"]
check_password_policy("correct horse battery staple", "ada")     -> []
check_password_policy("abcdefghijkl")                            -> []      # no composition rules
```

The tests import `check_password_policy`.

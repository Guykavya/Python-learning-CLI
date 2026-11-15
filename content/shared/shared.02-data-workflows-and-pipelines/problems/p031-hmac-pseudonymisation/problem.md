# Pseudonymise customer emails with HMAC

The analysts want to answer "how many orders does a typical customer place?" and "how many
customers came back in June?". For that they need **a stable customer identifier**, but not the
email address itself. Masking (`a***@example.com`) is not enough: `asha@` and `anil@` get the
same mask, so you cannot count customers with it.

The answer is a **pseudonym**: a value computed from the email that is

- **stable**: the same email always gives the same pseudonym, in every run, so joins and counts work;
- **one-way**: you cannot get the email back from it;
- **keyed**: nobody without the secret key can compute it.

A plain `hashlib.sha256(email)` is stable and one-way, but **not** keyed: anyone with a list of
likely emails (a leaked mailing list, say) hashes each one and looks the result up in your table.
That is a *dictionary attack*. An **HMAC** mixes a secret key into the hash: `hmac.new(key,
message, hashlib.sha256)`. Without the key, the dictionary attack is useless.

The key is a secret, so it never appears in code, in git or in logs. The pipeline reads it from
the environment variable `PAGEBOUND_PSEUDO_KEY`.

## Your task

In `solution.py` write three functions.

```python
def load_secret(env=None) -> bytes:
```

- Read `PAGEBOUND_PSEUDO_KEY` from `env` (any mapping); when `env` is `None`, from `os.environ`
  (read it when the function is called).
- Strip surrounding whitespace. If the variable is missing or empty, raise `RuntimeError` with a
  message that names `PAGEBOUND_PSEUDO_KEY`. Never fall back to a default key.
- If it is shorter than 16 characters, raise `RuntimeError` naming the variable, **without** the
  value in the message (error messages end up in logs).
- Return the value encoded as UTF-8 bytes.

```python
def pseudonymise(value: str | None, key: bytes) -> str | None:
```

`None` stays `None`. Otherwise strip and lower-case `value` (the same customer must always get the
same key), then return the first 16 characters of
`hmac.new(key, normalised.encode("utf-8"), hashlib.sha256).hexdigest()`.

```python
def pseudonymise_rows(rows, key, field="email", out_field="customer_key") -> list[dict]:
```

Return new rows where the column `field` is replaced by `out_field` (at the same position in the
dict) holding the pseudonym. A row without `field` gets `out_field = None` at the end. The input
rows are not changed, and no email remains anywhere in the output.

## Example

```python
key = b"test-key-0123456789"
pseudonymise("asha@example.com", key)          # '55671d1637abb1e4'
pseudonymise("  ASHA@example.com ", key)       # '55671d1637abb1e4'  (same customer)
pseudonymise("ravi@example.com", key)          # '38a2d145463f6be2'

pseudonymise_rows([{"id": 1, "email": "asha@example.com", "city": "Pune"}], key)
# [{'id': 1, 'customer_key': '55671d1637abb1e4', 'city': 'Pune'}]

load_secret({})        # RuntimeError: PAGEBOUND_PSEUDO_KEY is not set; ...
```

On your own machine you would set the key in the shell before running the pipeline, for example
`export PAGEBOUND_PSEUDO_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"`
(Windows PowerShell: `$env:PAGEBOUND_PSEUDO_KEY = "..."`), and keep it in a password manager:
lose the key and you can never compute the same pseudonyms again.

# Check a compose file

Chapter sections 6.2 (the file), 7.2 (the proxy edit: the API is no longer published) and 8.6 (log rotation), and "Try it: dependencies and readiness". Compose is never run by the tests, so you work on the **text** of `compose.yaml`, read with PyYAML (`yaml.safe_load`). Write a checker for the mistakes that cost people data or security.

## What to write

```python
def check_compose(yaml_text: str) -> list[tuple[str, str]]: ...
```

It returns `(service_name, code)` pairs, sorted, without duplicates. If the text is not a mapping with a non-empty `services:` mapping, raise `ValueError`.

Some words first. A service that has a `build:` key is built here. A **dependency** is any service named in another service's `depends_on` (list form or mapping form). The rules, exactly (these are the only rules):

| Code | Reported on | When |
|---|---|---|
| `depends-not-healthy` | the service that has the `depends_on` | a dependency is listed in the **list form** (`depends_on: [db]`), or in mapping form with a `condition` other than `service_healthy` (or no condition) |
| `no-healthcheck` | the dependency | it has no `healthcheck:` **and** no `build:` (a service built here may rely on the `HEALTHCHECK` of its Dockerfile, as the chapter's API does) |
| `dependency-port-published` | the dependency | it has a non-empty `ports:` (a database or an API behind a proxy must not be published to the host) |
| `data-not-in-named-volume` | the service that has the volume | one of its `volumes:` entries is an **anonymous** volume (`- /data`), a **writable bind mount** (the source starts with `.`, `/` or `~` and the mode does not contain `ro`), or a named volume that is **not declared** under the top-level `volumes:` |
| `inline-secret` | the service | an `environment:` entry (mapping form or `NAME=value` list form) whose name contains `SECRET`, `PASSWORD`, `PASSWD`, `TOKEN`, `API_KEY` or `PRIVATE_KEY`, or ends in `_KEY`, has a **non-empty literal** value. A value starting with `${` (a substitution), a missing value (`- NAME` or `NAME:` with nothing) and `env_file:` are fine |

A volume entry is `source:target` or `source:target:mode` (`ro`, `rw`). The long syntax (a mapping with `type`, `source`, `target`, `read_only`) is also allowed: `type: bind` without `read_only: true`, or `type: volume` with an undeclared source, is a finding.

## Example

```python
check_compose(CHAPTER_COMPOSE)        # the compose.yaml of chapter 6.2 (api + redis)
# []
check_compose("""
services:
  web:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_PASSWORD: hunter2
    volumes:
      - ./data:/data
    depends_on:
      - db
  db:
    image: postgres:16
    ports: ["5432:5432"]
""")
# [('db', 'dependency-port-published'), ('db', 'no-healthcheck'),
#  ('web', 'data-not-in-named-volume'), ('web', 'depends-not-healthy'), ('web', 'inline-secret')]
```

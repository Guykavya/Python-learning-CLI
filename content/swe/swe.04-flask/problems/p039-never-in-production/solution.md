## Approach

Separate three things the snippet mixes: **how the app runs** (`app.run`), **how it is configured** (`debug=True`, `SECRET_KEY = "dev"`) and **who can reach it** (`0.0.0.0`).

See `answer.md` for the model answer and the checklist.

Example of a safe start (the commands are exact; the output is not captured here):

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
gunicorn --workers 3 --timeout 30 --bind 127.0.0.1:8000 "app:create_app()"
# nginx listens on 443 with the TLS certificate and proxies to 127.0.0.1:8000
```

The key idea: the code you ship must behave the same in every environment; only the **configuration** (read from the environment) differs, and the dangerous settings default to *off*.

## Complexity

Not applicable.

## Another way

Containers: the same Gunicorn command inside a Docker image, with the platform's load balancer in front (swe.09). Or a platform that runs the WSGI app for you (a PaaS), which still expects you to keep debug off.

## Not covered

Health checks, graceful reloads (`SIGHUP`), and how many workers to run (usually `2 * CPU cores + 1`).

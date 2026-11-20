## Model answer

**1. `debug=True`.** It turns on the **Werkzeug interactive debugger**: when a view raises, the error page lets anyone who can open it run Python code in the stack frame (a console in the browser). An attacker who triggers any error therefore gets **remote code execution** on your server: they can read the environment (secrets, database passwords), the files, and open a shell. The PIN that protects the console is a convenience for developers, not security: it can be derived from information that leaks elsewhere and it is skipped when an attacker runs code another way. Even without the console, the debug error page shows source code, file paths, variable values and the config to every visitor. Debug mode also starts the reloader, which restarts the process when a file changes.

**2. The development server.** `app.run` is meant for one developer. It is not hardened against malformed or slow clients, it handles little traffic (a single process; threads at best), has no worker management, no graceful restarts, no TLS by default, and a crash or a slow request can block others. It also listens on `0.0.0.0` here, so it is open to the whole network (and port 80 needs root).

**3. What replaces it.** Run the app with **Gunicorn** (`gunicorn --workers 4 --timeout 30 "app:create_app()"`): a process manager that starts several worker processes, restarts crashed ones, enforces timeouts and imports the factory. Put a **reverse proxy** (nginx, Caddy, a cloud load balancer) in front: it terminates **TLS**, serves static files, buffers slow clients and passes requests to Gunicorn on a local port. Logs go to stdout and are collected by the platform.

**4. Keeping debug off.** The setting must come from the **environment/config**, with the safe value (`False`) as the default, and the production start command must not use `app.run`. The snippet also has a **hard-coded, known `SECRET_KEY`** (`"dev"`: anyone can forge sessions) and binds to `0.0.0.0` with `debug=True`; the secret must come from an environment variable, and a factory should refuse to start production with a default key.

**Checklist: your answer should mention**
- [ ] the debugger console runs code: **remote code execution** (PIN is not real security)
- [ ] debug pages leak source, paths, variables and config
- [ ] the dev server is single-purpose: little concurrency, not hardened, no TLS, no restarts
- [ ] **Gunicorn** with workers and timeouts, started with the factory (`"app:create_app()"`)
- [ ] a **reverse proxy** for TLS, static files and slow clients
- [ ] debug/secret settings from the environment; no `app.run` in production; the weak `SECRET_KEY`

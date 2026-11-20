## Hint 1

Re-read section 22.2: what exactly appears in the browser when a view raises with the debugger on? Who can see it, and what can they type into it?

## Hint 2

For the replacement, think of two programs: one that **runs your Python code in several processes** and one that **faces the internet**. Which of the two should speak TLS? Which should restart a crashed worker?

## Hint 3

```text
1. debugger = code execution for anyone who triggers an error; error page leaks source/config
2. dev server: little concurrency, not hardened, no TLS, no worker management
3. gunicorn --workers N "app:create_app()"  behind nginx (TLS, static files, slow clients)
4. debug from env, default off; no app.run; SECRET_KEY from env; do not bind 0.0.0.0 with debug
```

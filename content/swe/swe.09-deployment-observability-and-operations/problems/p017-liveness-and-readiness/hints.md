## Hint 1

Which of the two endpoints may touch the dependencies? Think about what the platform does when each fails: restart the process, or only stop sending traffic. Then write `/readyz` as: collect problems in a dict, return 503 if the dict is not empty.

## Hint 2

```text
/healthz: return {"status": "alive"}     (no checks, no state)
/readyz:  problems = {}
          if app.state.draining: problems["draining"] = "shutting down"
          for name, check in checks.items():
              try: check()
              except Exception as exc: problems[name] = str(exc) or type(exc).__name__
          if problems: JSONResponse({"status": "not ready", "problems": problems}, status_code=503)
          else: {"status": "ready"}
```

## Approach

The full code is `reference.py`: the chapter's Pagebound service (sections 5.1, 8, 9, 10) with the parts you wrote in p003, p013, p014, p017, p018 and p019 merged, and the three text constants taken from the chapter (5.2, 6.2 and 7.2, 11.4). The wiring that matters:

```python
def create_app(settings=None):
    settings = settings or Settings.from_env()
    configure_logging(settings.log_level)
    metrics = Metrics()

    @asynccontextmanager
    async def lifespan(app):
        ...create the table...
        log.info("starting", extra={"fields": {"version": settings.version, "env": settings.env}})
        yield
        app.state.draining = True                    # readiness goes red before we exit
        log.info("shutting down")

    app = FastAPI(..., lifespan=lifespan)
    app.state.draining = False
    app.add_middleware(RequestContext, metrics=metrics)
    ...routes...
```

How the tests prove the module's two outcomes and the chapter's checklist (15.5): a failing request is followed by its **id** through stdout JSON lines to the traceback (outcome 1, problem p015 as a function); the texts are judged by the same checkers as before; the service **drains** on shutdown and readiness turns red; the **database outage** turns readiness red but not liveness; the metrics count the 500 under a **route template**. Rolling back a bad deployment (outcome 2) is problems p025 to p027; what the project adds is that every release you would deploy this way is already **observable**: health, logs, metrics and a way back.

## Complexity

Per request: one regular-expression match, a few dictionary updates, one log line. The deployment texts cost nothing at run time; they are what lets a stranger run `docker compose up -d --wait` and get a working, monitored system.

## Another way

Add the rest of the chapter's stack as the next step on your machine: Nginx config with JSON access logs and rate limits (p010, p012), Prometheus and the alert rules (p020, p022), `deploy.sh` (p025), the backup job and a restore drill (p028), and a runbook per alert (p029). The tests here cover what runs in Python; the "Try it on your machine" blocks of the chapter cover the real tools.

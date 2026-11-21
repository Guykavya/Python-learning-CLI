## Hint 1

You have written every part already. Make a list of the parts and where each came from: settings (p003), JSON logs (p013), request-id middleware (p014), health (p017), draining (p018), metrics (p019), and the three texts (p006, p009, p023, with the chapter's own files as models). The new work is **wiring**: which object does the middleware need, where is the draining flag, what does the lifespan do at shutdown?

## Hint 2

```text
create_app(settings):
    configure_logging(settings.log_level); metrics = Metrics()
    lifespan: create the table; log "starting" with version and env; yield; app.state.draining = True; log "shutting down"
    app = FastAPI(lifespan=lifespan); app.state.draining = False
    app.add_middleware(RequestContext, metrics=metrics)      # request id, error answer, access log, metrics.observe_request
    routes: /, POST /orders, GET /orders/{order_id}, /boom, /healthz, /readyz, /metrics
```

## Hint 3

The three texts are the chapter's files (5.2, 6.2 with the proxy edit of 7.2, 11.4). Run the linters of p006, p009 and p023 on them as you write: they tell you what is missing. The compose file needs `api` (built here, named volume, log rotation, no ports) and `nginx` (ports on `127.0.0.1`, a read-only bind mount, `depends_on` with `service_healthy`).

## Hint 1

A record passes two gates: first the **logger's** level, then each **handler's** level. If the logger itself were at WARNING, the file handler could never see a DEBUG record. So which level must the logger have, and where does `verbose` go instead? For the "called twice" rule: where are the handlers stored (`logger.handlers`), and what must happen to a file handler before you drop it?

## Hint 2

```text
log = logging.getLogger("auto"); log.setLevel(DEBUG); log.propagate = False
for h in list(log.handlers): log.removeHandler(h); h.close()
console = StreamHandler(stream or sys.stderr)
console.setLevel([WARNING, INFO, DEBUG][min(verbose, 2)]); console.setFormatter(Formatter("%(levelname)s %(name)s: %(message)s"))
log.addHandler(console)
if logfile: fh = RotatingFileHandler(logfile, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
            fh.setLevel(DEBUG); fh.setFormatter(Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")); log.addHandler(fh)
return log
```

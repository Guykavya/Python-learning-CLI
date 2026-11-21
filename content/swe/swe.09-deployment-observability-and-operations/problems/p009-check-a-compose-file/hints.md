## Hint 1

First collect the facts: which services are dependencies (the names inside every `depends_on`, in list or mapping form), and which top-level volumes are declared. Then check each service for the rules that look at the service itself, and each dependency for the rules that look at the dependency.

## Hint 2

```text
data = yaml.safe_load(text); validate it is a dict with a non-empty services dict
declared = set(data.get("volumes") or {})
for each service:
    depends_on: list form -> finding; mapping form -> each entry must be {"condition": "service_healthy"}
    every volume entry: anonymous (no ":"), writable bind (source starts with . / ~ and no "ro"), or an undeclared name
    every environment item: name looks secret and value is non-empty and does not start with "${"
for each dependency: no healthcheck and no build -> finding; ports present -> finding
return sorted(set(findings))
```

`environment:` can be a mapping or a list of `NAME=value` strings: write one helper that turns both into `(name, value)` pairs.

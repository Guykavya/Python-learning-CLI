## Approach

Facts first, then rules. The full code is `reference.py`; its structure:

```python
def check_compose(yaml_text):
    data = yaml.safe_load(yaml_text)
    if not isinstance(data, dict) or not isinstance(data.get("services"), dict) or not data["services"]:
        raise ValueError("a compose file needs a services: mapping")
    services = {name: (svc or {}) for name, svc in data["services"].items()}
    declared = set(data.get("volumes") or {})
    findings, dependencies = set(), set()
    for name, svc in services.items():
        depends = svc.get("depends_on") or {}
        if isinstance(depends, list):                      # the list form cannot carry a condition
            dependencies.update(depends)
            if depends:
                findings.add((name, "depends-not-healthy"))
        else:
            for dep, config in depends.items():
                dependencies.add(dep)
                if not (isinstance(config, dict) and config.get("condition") == "service_healthy"):
                    findings.add((name, "depends-not-healthy"))
        ...                                                 # volumes and environment rules
    for dep in dependencies:
        ...                                                 # healthcheck and ports rules, reported on the dependency
    return sorted(findings)
```

Why each rule matters (all from the chapter): `service_healthy` removes the start-up race (6.2, "Try it"); a dependency published to the host can be reached around the proxy (7.2); data outside a named volume disappears with the container (4.4, 6.3); an inline secret is readable in `docker inspect` and in the file you commit (3.5).

## Complexity

O(size of the file).

## Another way

`docker compose config --quiet` validates the syntax and prints the resolved file (chapter 6.2), but it does not know your rules. Real policy checkers (for example `conftest` with OPA rules) run the same kind of checks on YAML in CI.

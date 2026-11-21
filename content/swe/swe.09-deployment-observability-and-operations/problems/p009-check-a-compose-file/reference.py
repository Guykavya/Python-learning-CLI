import yaml

SECRET_WORDS = ("SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY", "PRIVATE_KEY")


def _is_secret_name(name):
    name = name.upper()
    return any(word in name for word in SECRET_WORDS) or name.endswith("_KEY")


def _env_items(environment):
    if isinstance(environment, dict):
        return [(str(k), "" if v is None else str(v)) for k, v in environment.items()]
    items = []
    for entry in environment or []:
        name, _, value = str(entry).partition("=")
        items.append((name, value))
    return items


def _bad_volume(entry, declared):
    if isinstance(entry, dict):
        source = str(entry.get("source") or "")
        if entry.get("type") == "bind":
            return not entry.get("read_only")
        return not source or source not in declared
    parts = str(entry).split(":")
    if len(parts) == 1:
        return True                                            # anonymous volume
    source, mode = parts[0], (parts[2] if len(parts) > 2 else "")
    if source.startswith((".", "/", "~")):
        return "ro" not in mode.split(",")                     # a bind mount is fine only when read-only
    return source not in declared


def check_compose(yaml_text):
    data = yaml.safe_load(yaml_text)
    if not isinstance(data, dict) or not isinstance(data.get("services"), dict) or not data["services"]:
        raise ValueError("a compose file needs a services: mapping")
    services = {name: (svc or {}) for name, svc in data["services"].items()}
    declared = set(data.get("volumes") or {})
    findings, dependencies = set(), set()
    for name, svc in services.items():
        depends = svc.get("depends_on") or {}
        if isinstance(depends, list):
            dependencies.update(depends)
            if depends:
                findings.add((name, "depends-not-healthy"))
        else:
            for dep, config in depends.items():
                dependencies.add(dep)
                if not (isinstance(config, dict) and config.get("condition") == "service_healthy"):
                    findings.add((name, "depends-not-healthy"))
        if any(_bad_volume(v, declared) for v in svc.get("volumes") or []):
            findings.add((name, "data-not-in-named-volume"))
        if any(_is_secret_name(k) and v and not v.startswith("${") for k, v in _env_items(svc.get("environment"))):
            findings.add((name, "inline-secret"))
    for dep in dependencies:
        svc = services.get(dep)
        if svc is None:
            continue
        if not svc.get("healthcheck") and not svc.get("build"):
            findings.add((dep, "no-healthcheck"))
        if svc.get("ports"):
            findings.add((dep, "dependency-port-published"))
    return sorted(findings)

"""The three deployment checkers of this module, bundled so that the test can judge your DOCKERFILE, COMPOSE and WORKFLOW texts.
They are the reference solutions of problems p006 (lint_dockerfile), p009 (check_compose) and p023 (check_workflow): the same rules.
Your solution never imports this file."""
import re
import shlex
import types

import pytest
import yaml


RISKY_WORDS = ("SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY", "PRIVATE_KEY")


def _instructions(text):
    """Yield (first line number, KEYWORD, rest of the instruction), with backslash continuations joined."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        number, line = i + 1, lines[i].strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        while line.endswith("\\") and i < len(lines):
            line = line[:-1].rstrip() + " " + lines[i].strip()
            i += 1
        keyword, _, rest = line.partition(" ")
        yield number, keyword.upper(), rest.strip()


def _is_risky(name):
    name = name.upper()
    return any(word in name for word in RISKY_WORDS) or name.endswith("_KEY")


def _pairs(keyword, rest):
    try:
        tokens = shlex.split(rest)
    except ValueError:
        tokens = rest.split()
    if keyword == "ARG":
        return [tuple(token.split("=", 1)) for token in tokens if "=" in token]
    if tokens and all("=" in token for token in tokens):
        return [tuple(token.split("=", 1)) for token in tokens]
    if tokens:
        return [(tokens[0], " ".join(tokens[1:]))]                 # the old form: ENV NAME value
    return []


def lint_dockerfile(text):
    findings, stages = [], set()
    first_install = None
    copy_all_lines = []
    last_user = None
    for number, keyword, rest in _instructions(text):
        if keyword == "FROM":
            tokens = [t for t in rest.split() if not t.startswith("--")]
            image = tokens[0] if tokens else ""
            if len(tokens) >= 3 and tokens[1].lower() == "as":
                alias = tokens[2].lower()
            else:
                alias = None
            skip = image.lower() in stages or image == "scratch" or "$" in image or "@sha256:" in image
            if not skip:
                name = image.rsplit("/", 1)[-1]
                if ":" not in name or name.split(":", 1)[1] == "latest":
                    findings.append((number, "unpinned-base"))
            if alias:
                stages.add(alias)
            last_user = None                                        # only the last stage matters for USER
        elif keyword in ("CMD", "ENTRYPOINT"):
            if not rest.startswith("["):
                findings.append((number, "shell-cmd"))
        elif keyword in ("COPY", "ADD"):
            tokens = [t for t in rest.split() if not t.startswith("--")]
            sources = tokens[:-1]
            if any(source in (".", "./") for source in sources) and "--from=" not in rest:
                copy_all_lines.append(number)
        elif keyword == "RUN":
            if "pip install" in rest and first_install is None:
                first_install = number
            if ("apt-get install" in rest or "apt install" in rest) and "rm -rf /var/lib/apt/lists" not in rest:
                findings.append((number, "apt-no-cleanup"))
        elif keyword == "USER":
            last_user = rest.split()[0] if rest.split() else None
        elif keyword in ("ENV", "ARG"):
            for name, value in _pairs(keyword, rest):
                if _is_risky(name) and value and not value.startswith("$"):
                    findings.append((number, "secret-in-env"))
                    break
    if first_install is not None:
        findings += [(n, "copy-before-install") for n in copy_all_lines if n < first_install]
    if last_user is None or last_user.split(":")[0] in ("root", "0"):
        findings.append((0, "no-user"))
    return sorted(set(findings))


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


MOVING_REFS = {"main", "master", "latest", "HEAD"}


def check_workflow(workflow):
    problems = []
    triggers = workflow.get("on", workflow.get(True))            # YAML 1.1 reads the key `on` as the boolean True
    if not triggers:
        problems.append(("error", "no trigger: add an `on:` section"))
    if isinstance(triggers, dict) and "pull_request_target" in triggers:
        problems.append(("error", "pull_request_target runs with secrets on code from forks: avoid it"))
    if "permissions" not in workflow:
        problems.append(("warning", "no top-level permissions; the default token may be too powerful"))
    jobs = workflow.get("jobs") or {}
    if not jobs:
        problems.append(("error", "no jobs"))
    runs_make_test = False
    for name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        if "runs-on" not in job:
            problems.append(("error", f"job {name!r} has no runs-on"))
        if "timeout-minutes" not in job:
            problems.append(("warning", f"job {name!r} has no timeout-minutes; a hung job runs for 6 hours"))
        needs = job.get("needs") or []
        for need in ([needs] if isinstance(needs, str) else needs):
            if need not in jobs:
                problems.append(("error", f"job {name!r} needs {need!r}, which does not exist"))
        for i, step in enumerate(job.get("steps") or [], 1):
            if not isinstance(step, dict):
                continue
            uses, run = step.get("uses"), step.get("run") or ""
            if uses and not uses.startswith("./"):
                if "@" not in uses:
                    problems.append(("error", f"{name} step {i}: {uses!r} has no version after @ (no version pinned)"))
                else:
                    action, ref = uses.split("@", 1)
                    if ref in MOVING_REFS:
                        problems.append(("error", f"{name} step {i}: {uses!r} follows a moving branch; pin a version or a commit SHA"))
                    elif not action.startswith(("actions/", "docker/")) and not re.fullmatch(r"[0-9a-f]{40}", ref):
                        problems.append(("warning", f"{name} step {i}: third-party action {uses!r} should be pinned to a full commit SHA"))
                    if action == "actions/cache" and "hashFiles(" not in str((step.get("with") or {}).get("key", "")):
                        problems.append(("warning", f"{name} step {i}: the cache key does not use hashFiles(...) of the lock file"))
            if re.search(r"\$\{\{\s*secrets\.", run):
                problems.append(("error", f"{name} step {i}: a secret is pasted into a `run:` script; pass it through `env:`"))
            if re.search(r"\bmake\b[^\n]*\btest\b", run):
                runs_make_test = True
    if jobs and not runs_make_test:
        problems.append(("warning", "no step runs `make test`: CI should run the same command as developers"))
    return problems


@pytest.fixture
def checkers():
    return types.SimpleNamespace(lint_dockerfile=lint_dockerfile, check_compose=check_compose, check_workflow=check_workflow)

import re

MOVING_REFS = {"main", "master", "latest", "HEAD"}


def check(workflow):
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

import ast

LAYER_RANK = {"domain": 0, "services": 1, "infrastructure": 2, "web": 3}
EXTERNAL_BANS = {
    "domain": {"sqlite3", "fastapi", "httpx", "requests", "smtplib"},
    "services": {"sqlite3", "fastapi", "httpx", "requests", "smtplib"},
}


def violations(sources, layers, package="taskboard"):
    # TODO: ast.parse every source, collect project and external imports, apply the rule, return sorted unique pairs
    return []

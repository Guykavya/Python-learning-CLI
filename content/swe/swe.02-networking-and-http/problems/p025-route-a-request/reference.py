import re


def _compile(pattern):
    names = re.findall(r"\{(\w+)\}", pattern)
    regex = re.escape(pattern)
    for name in names:
        regex = regex.replace(re.escape("{" + name + "}"), f"(?P<{name}>[^/]+)")
    return re.compile("^" + regex + "$"), names


def route(routes, method, path):
    method = method.upper()
    patterns = {}
    for (m, pattern), handler in routes.items():
        patterns.setdefault(pattern, {})[m.upper()] = handler
    matches = []
    for pattern, handlers in patterns.items():
        regex, names = _compile(pattern)
        found = regex.match(path)
        if found:
            matches.append((len(names), pattern, handlers, found.groupdict()))
    matches.sort(key=lambda item: item[0])               # fewer parameters = more specific
    for _, pattern, handlers, params in matches:
        wanted = "GET" if method == "HEAD" and "HEAD" not in handlers else method
        if wanted in handlers:
            return 200, handlers[wanted], params
    if matches:
        allowed = sorted({m for _, _, handlers, _ in matches for m in handlers})
        return 405, None, {"Allow": ", ".join(allowed)}
    return 404, None, {}

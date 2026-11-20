def parse_status(text):
    result = {"staged": [], "modified": [], "deleted": [], "untracked": []}
    for line in text.splitlines():
        if not line.strip():
            continue
        x, y, path = line[0], line[1], line[3:]
        if " -> " in path:
            path = path.split(" -> ")[-1]
        if len(path) >= 2 and path[0] == '"' and path[-1] == '"':
            path = path[1:-1]
        if line.startswith("??"):
            result["untracked"].append(path)
            continue
        if x not in " ?":
            result["staged"].append(path)
        if y == "M":
            result["modified"].append(path)
        if "D" in (x, y):
            result["deleted"].append(path)
    return result

def plan_tree(rows):
    children = {}
    for node_id, parent, _unused, detail in rows:
        children.setdefault(parent, []).append((node_id, detail))
    lines = []
    stack = [(node, 0) for node in sorted(children.get(0, []), reverse=True)]
    while stack:
        (node_id, detail), depth = stack.pop()
        lines.append("  " * depth + detail)
        for child in sorted(children.get(node_id, []), reverse=True):
            stack.append((child, depth + 1))
    return "\n".join(lines)

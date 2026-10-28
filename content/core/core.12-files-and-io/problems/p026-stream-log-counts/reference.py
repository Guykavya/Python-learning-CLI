def count_levels(path):
    counts = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            level = parts[2]
            counts[level] = counts.get(level, 0) + 1
    return counts

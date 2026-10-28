import sys


def total_from_stdin():
    total = 0
    for line in sys.stdin:
        line = line.strip()
        if line == "":
            continue
        total += int(line)
    print(f"total: {total}")
    return total

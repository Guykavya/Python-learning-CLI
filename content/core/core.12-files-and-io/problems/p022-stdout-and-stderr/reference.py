import sys


def sum_numbers(items):
    total = 0
    for item in items:
        try:
            total += int(item)
        except ValueError:
            print(f"warning: skipping {item!r}", file=sys.stderr)
    print(f"total: {total}")
    return total

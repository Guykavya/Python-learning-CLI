import argparse
import sys


def words(line):
    word = []
    for ch in line.lower():
        if ch.isalpha() or ch == "'":
            word.append(ch)
        elif word:
            yield "".join(word)
            word = []
    if word:
        yield "".join(word)


def count_into(lines, counts):
    for line in lines:
        for w in words(line):
            counts[w] = counts.get(w, 0) + 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="wordfreq")
    parser.add_argument("files", nargs="*")
    parser.add_argument("-n", "--top", type=int, default=10)
    parser.add_argument("--min", type=int, default=1)
    args = parser.parse_args(argv)
    if args.top < 1:
        parser.error("-n must be at least 1")

    counts = {}
    for name in args.files or ["-"]:
        if name == "-":
            count_into(sys.stdin, counts)
        else:
            try:
                with open(name, encoding="utf-8") as f:
                    count_into(f, counts)
            except OSError:
                print(f"error: cannot read {name}", file=sys.stderr)
                return 2

    items = [(w, c) for w, c in counts.items() if c >= args.min]
    if not items:
        print("no words", file=sys.stderr)
        return 1
    items.sort(key=lambda item: (-item[1], item[0]))
    for w, c in items[: args.top]:
        print(w, c)
    return 0

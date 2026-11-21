import argparse
from pathlib import Path


def build_parser():
    p = argparse.ArgumentParser(prog="tidy", description="Tidy a folder safely.")
    p.add_argument("-v", "--verbose", action="count", default=0, help="more output (-vv for debug)")
    p.add_argument("--version", action="version", version="tidy 1.0")
    sub = p.add_subparsers(dest="command", required=True)

    org = sub.add_parser("organize", help="move files into folders by type")
    org.add_argument("folder", type=Path)
    org.add_argument("-n", "--dry-run", action="store_true", help="show what would happen, change nothing")

    und = sub.add_parser("undo", help="reverse the last 'organize'")
    und.add_argument("folder", type=Path)

    dup = sub.add_parser("dupes", help="list files with identical content")
    dup.add_argument("folder", type=Path)
    dup.add_argument("--min-size", type=int, default=1, metavar="BYTES", help="ignore smaller files")
    return p


if __name__ == "__main__":
    print(build_parser().parse_args())

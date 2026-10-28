import argparse


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="tidy")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--mode", choices=["copy", "move"], default="copy")
    return parser.parse_args(argv)

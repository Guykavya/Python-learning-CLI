import argparse
from pathlib import Path


def build_parser():
    p = argparse.ArgumentParser(prog="tidy", description="Tidy a folder safely.")
    # TODO: global -v/--verbose (counted) and --version
    # TODO: subcommands organize, undo, dupes (dest="command", required=True)
    return p


if __name__ == "__main__":
    print(build_parser().parse_args())

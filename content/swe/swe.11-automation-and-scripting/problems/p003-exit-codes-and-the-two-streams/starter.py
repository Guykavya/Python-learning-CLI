import argparse
import sys
from pathlib import Path


def list_files(folder, ext=None):
    """Names of the regular, non-hidden files directly in folder, sorted; filtered by suffix if ext is given."""
    # TODO
    return []


def build_parser():
    # TODO: prog="listfiles", positional folder (type=Path), option --ext
    return argparse.ArgumentParser(prog="listfiles")


def main(argv=None):
    # TODO: data to stdout, messages to stderr, return 0 / 1 (argparse gives 2 for usage errors)
    return 0


if __name__ == "__main__":
    sys.exit(main())

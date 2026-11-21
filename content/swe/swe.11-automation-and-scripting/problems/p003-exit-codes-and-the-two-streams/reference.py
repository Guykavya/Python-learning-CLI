import argparse
import sys
from pathlib import Path


def list_files(folder, ext=None):
    """Names of the regular, non-hidden files directly in folder, sorted; filtered by suffix if ext is given."""
    names = []
    for p in sorted(Path(folder).iterdir()):
        if p.is_file() and not p.name.startswith("."):
            if ext is None or p.suffix.lower() == ext.lower():
                names.append(p.name)
    return names


def build_parser():
    p = argparse.ArgumentParser(prog="listfiles", description="List the files in a folder.")
    p.add_argument("folder", type=Path)
    p.add_argument("--ext", help="only files with this suffix, such as .txt")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.folder.is_dir():
        print(f"listfiles: error: {args.folder} is not a folder", file=sys.stderr)
        return 1
    names = list_files(args.folder, args.ext)
    for name in names:
        print(name)
    print(f"{len(names)} file(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

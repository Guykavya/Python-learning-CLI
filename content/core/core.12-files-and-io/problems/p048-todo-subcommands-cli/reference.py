import argparse
import json
import sys
from pathlib import Path


def load(path):
    path = Path(path)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, todos):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def build_parser():
    parser = argparse.ArgumentParser(prog="todo")
    parser.add_argument("--file", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("text")
    p_add.add_argument("--priority", choices=["low", "normal", "high"], default="normal")

    p_list = sub.add_parser("list")
    group = p_list.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true")
    group.add_argument("--done", action="store_true")

    sub.add_parser("done").add_argument("id", type=int)
    sub.add_parser("remove").add_argument("id", type=int)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    todos = load(args.file)

    if args.command == "add":
        new_id = max((t["id"] for t in todos), default=0) + 1
        todos.append({"id": new_id, "text": args.text, "done": False, "priority": args.priority})
        save(args.file, todos)
        print(f"added {new_id}")
        return 0

    if args.command == "list":
        if args.all:
            shown = todos
        elif args.done:
            shown = [t for t in todos if t["done"]]
        else:
            shown = [t for t in todos if not t["done"]]
        if not shown:
            print("nothing to do")
            return 0
        for t in sorted(shown, key=lambda t: t["id"]):
            mark = "x" if t["done"] else " "
            print(f"{t['id']} [{mark}] {t['text']} ({t['priority']})")
        return 0

    target = [t for t in todos if t["id"] == args.id]
    if not target:
        print(f"no such id: {args.id}", file=sys.stderr)
        return 1
    if args.command == "done":
        target[0]["done"] = True
        print(f"done {args.id}")
    else:
        todos.remove(target[0])
        print(f"removed {args.id}")
    save(args.file, todos)
    return 0

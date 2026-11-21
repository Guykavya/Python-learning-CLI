import json
import shutil
from pathlib import Path

import click

# ---------------------------------------------------------------- the tidy library (given: the same core as the argparse tool)
CATEGORIES = {
    ".jpg": "images", ".jpeg": "images", ".png": "images", ".gif": "images",
    ".pdf": "documents", ".docx": "documents", ".txt": "documents",
    ".csv": "data", ".xlsx": "data", ".json": "data",
    ".zip": "archives", ".tar": "archives", ".gz": "archives",
    ".mp3": "audio", ".wav": "audio",
}
JOURNAL = ".tidy-journal.json"


def category_for(path):
    return CATEGORIES.get(Path(path).suffix.lower(), "other")


def unique_destination(dst):
    """Never overwrite: if 'a.txt' exists, use 'a (1).txt', 'a (2).txt'..."""
    if not dst.exists():
        return dst
    n = 1
    while True:
        candidate = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def plan_moves(root):
    """Decide what to move where. Changes nothing. Only files directly in `root`, no hidden ones."""
    moves = []
    for src in sorted(Path(root).iterdir()):
        if src.is_file() and not src.name.startswith("."):
            moves.append((src, unique_destination(Path(root) / category_for(src) / src.name)))
    return moves


def apply_moves(moves, root, dry_run=False):
    """Do the moves (unless dry_run) and write a journal so they can be undone."""
    done = []
    for src, dst in moves:
        if not dry_run:
            dst.parent.mkdir(exist_ok=True)
            shutil.move(str(src), str(dst))
        done.append((src, dst))
    if done and not dry_run:
        (Path(root) / JOURNAL).write_text(json.dumps([[str(s), str(d)] for s, d in done]), encoding="utf-8")
    return done


def undo(root):
    """Put every file back where the journal says it came from."""
    journal = Path(root) / JOURNAL
    if not journal.exists():
        return []
    restored = []
    for s, d in reversed(json.loads(journal.read_text(encoding="utf-8"))):
        s, d = Path(s), Path(d)
        if d.exists() and not s.exists():
            shutil.move(str(d), str(s))
            restored.append((d, s))
            try:
                d.parent.rmdir()                    # remove the category folder if it is now empty
            except OSError:
                pass                                # not empty: leave it alone
    journal.unlink()
    return restored


# ---------------------------------------------------------------- the Click front end

@click.group()
@click.version_option("1.0", prog_name="tidy")
def cli():
    """Tidy a folder safely."""


@cli.command("organize")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("-n", "--dry-run", is_flag=True, help="Show what would happen, change nothing.")
def organize_command(folder, dry_run):
    """Move files into folders by type."""
    label = "would move" if dry_run else "moved"
    for src, dst in apply_moves(plan_moves(folder), folder, dry_run):
        click.echo(f"{label}: {src.name} -> {dst.relative_to(folder).as_posix()}")


@cli.command("undo")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.confirmation_option(prompt="Put all moved files back?")
def undo_command(folder):
    """Reverse the last organize."""
    click.echo(f"restored {len(undo(folder))} file(s)")


if __name__ == "__main__":
    cli()

"""Read a chapter in the terminal, one `## ` section at a time, with coloured markdown."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass

from learn import ui

_CODE_SPAN = re.compile(r"(`[^`]+`)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BULLET = re.compile(r"^(\s*)[-*] (.*)$")
_DETAILS = re.compile(r"^<details>\s*<summary>(.*)</summary>\s*$")


@dataclass
class Section:
    title: str
    lines: list[str]


def split_sections(text: str) -> list[Section]:
    """Split at `## ` headings. Lines inside ``` fences never start a section."""
    sections: list[Section] = []
    title, buf, in_code = "Introduction", [], False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        elif not in_code and line.startswith("## "):
            if any(s.strip() for s in buf):
                sections.append(Section(title, buf))
            title, buf = line[3:].strip(), []
        buf.append(line)
    if any(s.strip() for s in buf):
        sections.append(Section(title, buf))
    return sections


def _inline(text: str) -> str:
    parts = []
    for part in _CODE_SPAN.split(text):
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            parts.append(ui.accent(part[1:-1]))
        else:
            part = _BOLD.sub(lambda m: ui.bold(m.group(1)), part)
            part = _LINK.sub(lambda m: ui.style(m.group(1), "blue") + ui.dim(f" ({m.group(2)})"), part)
            parts.append(part)
    return "".join(parts)


def _render_line(line: str) -> list[str]:
    width = min(ui.terminal_width(), 100)
    if line.startswith("# "):
        return [ui.style(line[2:].upper(), "bold", "yellow")]
    if line.startswith("## "):
        return [ui.style(line[3:], "bold", "cyan"), ui.dim("━" * min(len(line) + 2, width))]
    if line.startswith("### "):
        return [ui.bold(_inline(line[4:]))]
    if line.startswith("#### "):
        return [ui.style(line[5:], "bold", "dim")]
    if line.strip() in ("---", "***"):
        return [ui.dim("─" * width)]
    if line.startswith(">"):
        return [ui.dim("┃ ") + _inline(line.lstrip(">").strip())]
    if line.startswith("|"):
        if set(line) <= set("|-: "):
            return [ui.dim(line)]
        return [_inline(line).replace("|", ui.dim("│"))]
    m = _BULLET.match(line)
    if m:
        return [f"{m.group(1)}  • {_inline(m.group(2))}"]
    return [_inline(line)]


def _code_block(code: list[str], lang: str) -> list[str]:
    if code and code[0].startswith(">>> "):
        lang = "pycon"
    body = "\n".join(code)
    if ui.color_enabled() and lang in ("python", "py", "pycon", "bash", "sh", "json", "toml", "yaml"):
        try:
            from pygments import highlight
            from pygments.formatters import TerminalFormatter
            from pygments.lexers import get_lexer_by_name

            body = highlight(body, get_lexer_by_name(lang, stripnl=False), TerminalFormatter()).rstrip("\n")
        except Exception:  # an unknown lexer or a missing pygments just means no colour
            pass
    bar = ui.dim("│ ")
    return [bar + line for line in body.split("\n")]


def _summary(text: str) -> str:
    return text.replace("<code>", "`").replace("</code>", "`")


def has_answers(lines: list[str]) -> bool:
    return any(_DETAILS.match(line) for line in lines)


def render(lines: list[str], reveal: bool = False) -> str:
    """Markdown to coloured text. `<details>` answers stay hidden unless `reveal` is set."""
    out: list[str] = []
    code: list[str] | None = None
    lang = ""
    hiding = False
    for line in lines:
        details = _DETAILS.match(line) if code is None else None
        if details:
            label = _inline(_summary(details.group(1)))
            if reveal:
                out.append(ui.style("▾ ", "yellow") + ui.bold(label))
            else:
                out.append(ui.style("▸ ", "yellow") + label + ui.dim("  (hidden: type a after this section)"))
                hiding = True
            continue
        if code is None and line.strip() == "</details>":
            hiding = False
            continue
        if hiding:
            continue
        if line.startswith("```"):
            if code is None:
                code, lang = [], line[3:].strip().lower()
            else:
                out.extend(_code_block(code, lang))
                code = None
            continue
        if code is not None:
            code.append(line)
        else:
            out.extend(_render_line(line))
    if code is not None:
        out.extend(_code_block(code, lang))
    return "\n".join(out)


def _page(text: str) -> None:
    """Show text through `less` when it is longer than the screen, otherwise print it."""
    less = shutil.which("less")
    if not less or not sys.stdout.isatty():
        print(text)
        return
    subprocess.run([less, "-R", "-F", "-X"], input=text, text=True)


def contents(sections: list[Section], current: int) -> None:
    ui.heading("Contents")
    for i, s in enumerate(sections, 1):
        mark = ui.accent("▶") if i - 1 == current else " "
        print(f"  {mark} {i:>2}. {s.title}")


def read_chapter(title: str, text: str, start: int, save: Callable[[int], None]) -> None:
    """The reading loop. `save` is called with the section index each time one is shown."""
    sections = split_sections(text)
    i = max(0, min(start, len(sections) - 1))
    reveal = False
    if start > 0:
        print(ui.dim("Continuing where you stopped. Type c for the contents or 1 to start over.\n"))
    while True:
        s = sections[i]
        save(i)
        header = ui.dim(f"{title}  ·  section {i + 1} of {len(sections)}")
        footer = ui.dim(f"\n── end of section {i + 1}/{len(sections)} ──")
        _page(header + "\n\n" + render(s.lines, reveal) + footer)
        nxt = f"next: {sections[i + 1].title}" if i + 1 < len(sections) else "this was the last section"
        print(ui.dim(f"  {nxt}"))
        answers = " · a answers" if has_answers(s.lines) and not reveal else ""
        choice = ui.ask(f"  [Enter] next · p previous · c contents · number jump{answers} · q quit").lower()
        reveal = choice == "a" and bool(answers)
        if reveal:
            continue
        if choice in ("q", "quit"):
            return
        if choice == "c":
            contents(sections, i)
            pick = ui.ask("  Section number (Enter to stay)")
            if pick.isdigit() and 1 <= int(pick) <= len(sections):
                i = int(pick) - 1
            continue
        if choice == "p":
            i = max(0, i - 1)
        elif choice.isdigit() and 1 <= int(choice) <= len(sections):
            i = int(choice) - 1
        elif choice == "":
            if i + 1 >= len(sections):
                print(ui.ok("  Chapter finished. ") + ui.dim("Practise it with: learn next"))
                return
            i += 1

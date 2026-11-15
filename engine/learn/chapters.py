"""Tools for chapter.md files: parse them into blocks, lint them, run their code, pull out the files they write, and make flashcards.

A chapter is Markdown with fenced code blocks. Two conventions matter here:
  ```python run   a block the chapter's output was produced from. Blocks of one chapter share one namespace, in order.
  ```text         the output pasted under it.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path

OPEN_FENCE = re.compile(r"^( {0,3})(`{3,})\s*([^`]*?)\s*$")


@dataclass
class Block:
    info: str            # the text after the opening fence, e.g. "python run"
    code: str
    start: int           # 1-based line of the opening fence
    end: int             # 1-based line of the closing fence (0 if never closed)

    @property
    def is_python_run(self) -> bool:
        return self.info.split() == ["python", "run"]


def parse_blocks(text: str) -> tuple[list[Block], int]:
    """Return the fenced blocks of a chapter and the line of an unclosed fence (0 if every fence closes).
    Fences inside blockquotes ('> ```') and inline triple backticks are not fences."""
    blocks: list[Block] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = OPEN_FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        length, info, start = len(m.group(2)), m.group(3), i + 1
        j = i + 1
        body: list[str] = []
        closed = False
        while j < len(lines):
            c = re.match(r"^ {0,3}(`{3,})\s*$", lines[j])
            if c and len(c.group(1)) >= length:
                closed = True
                break
            body.append(lines[j])
            j += 1
        if not closed:
            return blocks, start
        blocks.append(Block(info, "\n".join(body), start, j + 1))
        i = j + 1
    return blocks, 0


# ---------------------------------------------------------------- text-file encoding (a Windows hazard)

def _line_offsets(source: str) -> list[int]:
    offsets, total = [], 0
    for line in source.splitlines(keepends=True):
        offsets.append(total)
        total += len(line)
    return offsets


def _index(source: str, offsets: list[int], lineno: int, col_utf8: int) -> int:
    line = source.splitlines(keepends=True)[lineno - 1]
    return offsets[lineno - 1] + len(line.encode("utf-8")[:col_utf8].decode("utf-8"))


def _text_io_calls(tree: ast.AST):
    """Calls that read or write TEXT files without saying which encoding: open(...), Path.write_text, Path.read_text."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        has_enc = any(k.arg == "encoding" for k in node.keywords)
        if isinstance(f, ast.Attribute) and f.attr == "write_text" and not has_enc and len(node.args) < 2:
            yield node, "write_text"
        elif isinstance(f, ast.Attribute) and f.attr == "read_text" and not has_enc and len(node.args) < 1:
            yield node, "read_text"
        elif isinstance(f, ast.Name) and f.id == "open" and not has_enc:
            mode = None
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = node.args[1].value
            for k in node.keywords:
                if k.arg == "mode" and isinstance(k.value, ast.Constant):
                    mode = k.value.value
            if mode is None or "b" not in str(mode):
                yield node, "open"
        elif (isinstance(f, ast.Attribute) and f.attr in ("run", "Popen", "check_output")
              and isinstance(f.value, ast.Name) and f.value.id == "subprocess" and not has_enc
              and any(k.arg in ("text", "universal_newlines") and isinstance(k.value, ast.Constant) and k.value.value is True
                      for k in node.keywords)):
            yield node, "subprocess." + f.attr


def _payload_of(node: ast.Call) -> ast.Constant | None:
    """The string a write_text call writes, if it is a literal for a .py file (we check the code inside it too)."""
    if not (isinstance(node.func, ast.Attribute) and node.func.attr == "write_text" and node.args):
        return None
    arg = node.args[0]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg
    return None


def encoding_issues(code: str, prefix: str = "") -> list[tuple[int, str]]:
    """(line, message) for every text-file call without encoding=, including inside code written to .py files."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    out = []
    for node, kind in _text_io_calls(tree):
        out.append((node.lineno, f"{prefix}{kind}() without encoding='utf-8' (Windows uses a different default)"))
    for node in ast.walk(tree):                                  # code written to a file is checked too, whether or not the writing call is itself fine
        payload = _payload_of(node) if isinstance(node, ast.Call) else None
        if payload is not None and "import" in payload.value:
            out += encoding_issues(payload.value, prefix=f"{prefix}inside the file written at line {node.lineno}: ")
    return sorted(out)


def fix_encoding(code: str) -> str:
    """Add encoding='utf-8' to every text-file call (also inside raw triple-quoted code written to files). Returns new source."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    offsets = _line_offsets(code)
    edits: list[tuple[int, int, str]] = []                         # (start, end, replacement) on the ORIGINAL source
    for node, kind in _text_io_calls(tree):
        end = _index(code, offsets, node.end_lineno, node.end_col_offset) - 1      # the closing parenthesis
        inner = code[_index(code, offsets, node.lineno, node.col_offset):end].rstrip()
        sep = "" if inner.endswith("(") else ", "
        edits.append((end, end, f'{sep}encoding="utf-8"'))
    for node in ast.walk(tree):
        payload = _payload_of(node) if isinstance(node, ast.Call) else None
        if payload is not None and "import" in payload.value:
            s = _index(code, offsets, payload.lineno, payload.col_offset)
            e = _index(code, offsets, payload.end_lineno, payload.end_col_offset)
            literal = code[s:e]
            m = re.match(r"^(r?)(\'\'\'|\"\"\")(.*)(\'\'\'|\"\"\")$", literal, re.S)
            if m and m.group(2) == m.group(4) and (m.group(1) == "r" or "\\" not in m.group(3)):      # a plain string is safe to edit only if it has no escapes
                fixed = fix_encoding(m.group(3))
                if fixed != m.group(3):
                    edits.append((s + len(m.group(1)) + 3, e - 3, fixed))
    for start, end, repl in sorted(edits, key=lambda t: -t[0]):
        code = code[:start] + repl + code[end:]
    return code


def fix_chapter_encoding(text: str) -> tuple[str, int]:
    """fix_encoding() on every python code block of a chapter. Returns (new text, number of blocks changed)."""
    blocks, unclosed = parse_blocks(text)
    if unclosed:
        return text, 0
    lines = text.splitlines()
    changed = 0
    for b in reversed(blocks):
        if b.info.split()[:1] != ["python"]:
            continue
        fixed = fix_encoding(b.code)
        if fixed != b.code:
            lines[b.start:b.end - 1] = fixed.split("\n")
            changed += 1
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), changed


# ---------------------------------------------------------------- lint

@dataclass
class Issue:
    line: int
    level: str        # "error" or "warning"
    rule: str
    message: str

    def __str__(self) -> str:
        return f"line {self.line}: {self.level}: [{self.rule}] {self.message}"


def lint_chapter(text: str) -> list[Issue]:
    issues: list[Issue] = []
    raw_lines = text.splitlines()
    blocks, unclosed = parse_blocks(text)
    if unclosed:
        issues.append(Issue(unclosed, "error", "fence", "a code fence is opened here and never closed (everything after it renders as code)"))
        return issues
    inside = set()
    for b in blocks:
        inside.update(range(b.start, b.end + 1))
    # prose only: lines outside every code block (code may contain '# comments', '## ' strings and html)
    lines = [l if (n not in inside) else "" for n, l in enumerate(raw_lines, 1)]
    # inline triple backticks inside prose break the reader
    for n, line in enumerate(lines, 1):
        if "```" in line and not line.lstrip().startswith(">"):
            issues.append(Issue(n, "error", "inline-fence", "triple backticks in the middle of a line: use single backticks for inline code"))
    # code blocks: syntax, output blocks, encoding
    for idx, b in enumerate(blocks):
        if b.is_python_run:
            try:
                ast.parse(b.code)
            except SyntaxError as exc:
                issues.append(Issue(b.start + (exc.lineno or 0), "error", "syntax", f"a 'python run' block does not parse: {exc.msg}"))
                continue
            nxt = blocks[idx + 1] if idx + 1 < len(blocks) else None
            if nxt is not None and nxt.info == "text" and nxt.start <= b.end + 2 and not nxt.code.strip():
                issues.append(Issue(nxt.start, "error", "empty-output", "the output block under a 'python run' block is empty"))
            for ln, msg in encoding_issues(b.code):
                issues.append(Issue(b.start + ln, "warning", "encoding", msg))
    # details boxes
    opens = [n for n, l in enumerate(lines, 1) if "<details>" in l]
    closes = [n for n, l in enumerate(lines, 1) if "</details>" in l]
    if len(opens) != len(closes):
        issues.append(Issue(opens[-1] if opens else 1, "error", "details", f"{len(opens)} <details> but {len(closes)} </details>"))
    for n in opens:
        if not lines[n - 1].lstrip().startswith("<details>") or lines[n - 1].startswith(">"):
            issues.append(Issue(n, "error", "details", "<details> must start its own line, outside any blockquote (the reader hides answers only then)"))
    for n in closes:
        if lines[n - 1].strip() != "</details>":
            issues.append(Issue(n, "error", "details", "</details> must be on its own line"))
    # Visualise-it boxes
    vis = [n for n, l in enumerate(lines, 1) if l.startswith("> **Visualise it**")]
    for n in vis:
        if n >= len(lines) or not lines[n].startswith('> "'):
            issues.append(Issue(n, "error", "visualise", 'the line after "Visualise it" must be the quoted prompt (> "...")'))
        elif n + 1 < len(lines) and lines[n + 1].strip() != "":
            issues.append(Issue(n + 1, "error", "visualise", "leave a blank line after a Visualise-it box"))
    if not vis:
        issues.append(Issue(1, "warning", "visualise", "no optional 'Visualise it' prompt boxes in this chapter"))
    # structure: the terminal reader pages by '## '
    if sum(1 for l in lines if l.startswith("# ")) != 1:
        issues.append(Issue(1, "error", "title", "a chapter needs exactly one '# ' title line"))
    if sum(1 for l in lines if l.startswith("## ")) < 3:
        issues.append(Issue(1, "error", "sections", "fewer than three '## ' sections (the reader pages by them)"))
    return issues


# ---------------------------------------------------------------- run the code of a chapter

DRIVER = r'''
import contextlib, io, json, sys, time, traceback
blocks = json.load(open(sys.argv[1], encoding="utf-8"))
diff_mode = sys.argv[2] == "diff"
g = {"__name__": "__main__"}
results = []
for b in blocks:
    buf = io.StringIO()
    t0 = time.perf_counter()
    status, err = "ok", ""
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(b["code"], f"<chapter line {b['line']}>", "exec"), g)
    except BaseException:
        status, err = "FAILED", traceback.format_exc()
    results.append({"line": b["line"], "status": status, "seconds": round(time.perf_counter() - t0, 2), "error": err, "output": buf.getvalue() if diff_mode else ""})
    if status == "FAILED" and b.get("stop", True):
        break
json.dump(results, open(sys.argv[3], "w", encoding="utf-8"))
'''


@dataclass
class VerifyResult:
    blocks: int = 0
    ran: int = 0
    failed: list[tuple[int, str]] = field(default_factory=list)
    seconds: float = 0.0
    same_output: int = 0
    different_output: list[int] = field(default_factory=list)


def _normalise_output(text: str) -> list[str]:
    return [l.rstrip() for l in text.strip().splitlines()]


def verify_chapter(text: str, timeout: float = 600.0, diff: bool = False, strict_encoding: bool = False) -> VerifyResult:
    """Run every 'python run' block of a chapter, in order, in one fresh process and one shared namespace."""
    blocks, _ = parse_blocks(text)
    runnable = [(i, b) for i, b in enumerate(blocks) if b.is_python_run]
    result = VerifyResult(blocks=len(runnable))
    with tempfile.TemporaryDirectory(prefix="learn_verify_") as tmp:
        tmpd = Path(tmp)
        (tmpd / "blocks.json").write_text(json.dumps([{"code": b.code, "line": b.start} for _, b in runnable]), encoding="utf-8")
        (tmpd / "driver.py").write_text(DRIVER, encoding="utf-8")
        cmd = [sys.executable]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        if strict_encoding:
            env.pop("PYTHONUTF8", None)
            env["PYTHONUTF8"] = "0"
            cmd += ["-X", "warn_default_encoding", "-W", "error::EncodingWarning"]
        else:
            env["PYTHONUTF8"] = "1"
        cmd += [str(tmpd / "driver.py"), str(tmpd / "blocks.json"), "diff" if diff else "plain", str(tmpd / "out.json")]
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(cmd, cwd=tmpd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            result.failed.append((0, f"timed out after {timeout:.0f} s"))
            return result
        result.seconds = time.perf_counter() - t0
        out_path = tmpd / "out.json"
        if not out_path.exists():
            result.failed.append((0, (proc.stderr or proc.stdout)[-800:]))
            return result
        rows = json.loads(out_path.read_text(encoding="utf-8"))
    result.ran = sum(1 for r in rows if r["status"] == "ok")
    for r in rows:
        if r["status"] == "FAILED":
            result.failed.append((r["line"], r["error"].strip().splitlines()[-1] if r["error"].strip() else "failed"))
    if diff:
        by_line = {b.start: (i, b) for i, b in runnable}
        for r in rows:
            if r["status"] != "ok":
                continue
            i, b = by_line[r["line"]]
            nxt = blocks[i + 1] if i + 1 < len(blocks) else None
            if nxt is not None and nxt.info == "text" and nxt.start <= b.end + 2:
                if _normalise_output(nxt.code) == _normalise_output(r["output"]):
                    result.same_output += 1
                else:
                    result.different_output.append(r["line"])
    return result


# ---------------------------------------------------------------- files that a chapter writes

@dataclass
class ExtractedFile:
    root: str            # the variable the path starts from, e.g. "pkg" or "proj"
    relpath: str
    content: str


def _path_parts(node: ast.AST) -> tuple[str, list[str]] | None:
    """(root variable, [parts]) for expressions like  pkg / "app" / "main.py"."""
    parts: list[str] = []
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if not (isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)):
            return None
        parts.append(node.right.value)
        node = node.left
    if isinstance(node, ast.Name) and parts:
        return node.id, list(reversed(parts))
    return None


def extract_files(text: str) -> list[ExtractedFile]:
    """Files that 'python run' blocks write with  (root / "name.py").write_text("...")  and a literal string."""
    found: list[ExtractedFile] = []
    for b in parse_blocks(text)[0]:
        if not b.is_python_run:
            continue
        try:
            tree = ast.parse(b.code)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "write_text" and node.args
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                target = _path_parts(node.func.value)
                if target:
                    found.append(ExtractedFile(target[0], "/".join(target[1]), node.args[0].value))
    return found


def write_extracted(files: list[ExtractedFile], out_dir: Path, force: bool = False) -> tuple[list[Path], list[Path]]:
    """Write files under out_dir/<root>/<path>. Returns (written, skipped because they already exist)."""
    written, skipped = [], []
    for f in files:
        base = (out_dir / f.root).resolve()
        dest = (base / f.relpath).resolve()
        if base not in dest.parents:
            continue                                               # a path like ../x.py must never leave its folder
        if dest.exists() and not force:
            skipped.append(dest)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f.content if f.content.endswith("\n") else f.content + "\n", encoding="utf-8", newline="\n")
        written.append(dest)
    return written, skipped


# ---------------------------------------------------------------- flashcards from the question-and-answer boxes

@dataclass
class Card:
    front: str
    back: str
    section: str


def _numbered(text: str) -> dict[int, str]:
    items: dict[int, str] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if m:
            current = int(m.group(1))
            items[current] = m.group(2).strip()
        elif current is not None and line.strip() and not line.startswith("#"):
            items[current] += " " + line.strip()
        elif not line.strip():
            current = current if current is None else current          # blank lines inside a numbered item are allowed
    return items


def make_cards(text: str) -> list[Card]:
    """One card per question that has an answer in the <details> box that follows it. Pairs items by their numbers."""
    lines = text.splitlines()
    cards: list[Card] = []
    section = ""
    last_heading = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^#{2,4} ", line):
            section, last_heading = re.sub(r"^#+\s*", "", line), i
        if line.startswith("<details>"):
            j = i
            while j < len(lines) and "</details>" not in lines[j]:
                j += 1
            body = "\n".join(lines[i + 1:j])
            answers = _numbered(body)
            before = [l for l in lines[last_heading + 1:i] if not l.startswith(">")]
            questions = _numbered("\n".join(before))
            paired = [(questions[n], a) for n, a in answers.items() if n in questions and len(questions[n]) > 8]
            for q, a in paired:
                cards.append(Card(q, a, section))
            if not paired and re.sub(r"<[^>]+>", "", body).strip():
                prompt = "\n".join(before).strip()                              # e.g. a 'Predict the output' code block
                answer = re.sub(r"^<details><summary>.*?</summary>", "", "\n".join(lines[i:j]), flags=re.S).strip()
                if len(prompt) > 15 and len(prompt) <= 1500 and len(answer) <= 2500:
                    heading = re.sub(r"^\d+(\.\d+)*\s*", "", section) or "Question"
                    cards.append(Card(f"{heading}\n\n{prompt}", answer, section))
            i = j
        i += 1
    return cards

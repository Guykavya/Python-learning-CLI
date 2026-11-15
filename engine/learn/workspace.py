"""Full-screen problem workspace (`learn work [problem]`), built with Textual (optional extra `[tui]`).

The statement stays on the left; your file, hints, check result and walkthrough are tabs on the right.
You still write code in your own editor (`e` opens VS Code); the "My file" tab refreshes when you save.

Every action calls the same command the plain CLI uses (`cmd_check`, `cmd_hint`, `cmd_solution`,
`cmd_stuck`) and captures what it prints, so scoring, hint counting, reviews and the
"attempt before solution" rule are exactly the same in both interfaces.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import shutil
from collections.abc import Callable
from pathlib import Path

from rich.console import Group
from rich.syntax import Syntax
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Label, Markdown, Static, TabbedContent, TabPane

from learn import cli, content, db, runner


def run_command(func: Callable[[argparse.Namespace], None], width: int, **options) -> tuple[str, str | None]:
    """Run a CLI command, returning (what it printed, the UserError message or None)."""
    args = argparse.Namespace(problem=None, review=False, code=False, force=False, rate=None)
    vars(args).update(options)
    out = io.StringIO()
    old_columns = os.environ.get("COLUMNS")
    os.environ["COLUMNS"] = str(max(width, 40))  # boxes like the solve screen fit the panel, not the terminal
    error = None
    try:
        with contextlib.redirect_stdout(out):
            func(args)
    except cli.UserError as exc:
        error = str(exc)
    finally:
        if old_columns is None:
            os.environ.pop("COLUMNS", None)
        else:
            os.environ["COLUMNS"] = old_columns
    return out.getvalue(), error


DIALOG_CSS = """
#dialog { width: 80%; max-width: 100; height: auto; max-height: 90%;
          border: thick $primary; background: $surface; padding: 1 2; }
#dialog VerticalScroll { height: auto; max-height: 24; }
#buttons { height: auto; margin-top: 1; }
#buttons Button { margin-right: 2; }
"""


class ConfirmScreen(ModalScreen[bool]):
    """Yes / no question. Enter or y = yes, Escape or n = no."""

    CSS = "ConfirmScreen { align: center middle; }" + DIALOG_CSS
    BINDINGS = [Binding("y", "answer(True)", "Yes"), Binding("n,escape", "answer(False)", "No")]

    def __init__(self, message: str, yes: str, no: str) -> None:
        super().__init__()
        self.message, self.yes, self.no = message, yes, no

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.message)
            with Horizontal(id="buttons"):
                yield Button(f"{self.yes} (y)", id="yes", variant="warning")
                yield Button(f"{self.no} (n)", id="no", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#no", Button).focus()  # the safe choice has focus

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

    def action_answer(self, value: bool) -> None:
        self.dismiss(value)


class RateScreen(ModalScreen["int | None"]):
    """Explain problems: show the model answer, then the learner rates their own explanation."""

    CSS = "RateScreen { align: center middle; }" + DIALOG_CSS
    BINDINGS = [
        Binding("1", "rate(1)", "Missed key ideas"),
        Binding("2", "rate(2)", "Mostly right"),
        Binding("3", "rate(3)", "Fully covered"),
        Binding("escape", "rate(0)", "Cancel"),
    ]

    def __init__(self, model_answer: str) -> None:
        super().__init__()
        self.model_answer = model_answer

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("[b]Model answer[/b]  Compare it honestly with yours.")
            with VerticalScroll():
                yield Markdown(self.model_answer, open_links=False)
            with Horizontal(id="buttons"):
                yield Button("1 Missed key ideas", id="r1", variant="error")
                yield Button("2 Mostly right", id="r2", variant="warning")
                yield Button("3 Fully covered", id="r3", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(int(event.button.id[1]))

    def action_rate(self, value: int) -> None:
        self.dismiss(value or None)


class WorkspaceApp(App[None]):
    TITLE = "learn work"
    CSS = """
    #status { height: 1; padding: 0 1; background: $boost; }
    #statement { width: 1fr; padding: 0 1; border-right: solid $primary-darken-2; }
    #side { width: 1fr; }
    .pane { padding: 0 1; }
    """
    BINDINGS = [
        Binding("c", "check", "Check"),
        Binding("h", "hint", "Hint"),
        Binding("s", "solution", "Solution"),
        Binding("x", "stuck", "Stuck prompt"),
        Binding("e", "editor", "Open in editor"),
        Binding("f", "tab('tab-file')", "My file"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, problem_id: str) -> None:
        super().__init__()
        self.prob = content.get(problem_id)
        self.busy = False
        self._file_stamp: tuple[float, int] | None = None

    # --- state from the tracker --------------------------------------------------------------

    def state(self):
        conn = db.connect()
        try:
            return db.problem_state(conn, self.prob.id)
        finally:
            conn.close()

    @property
    def work_dir(self) -> Path:
        st = self.state()
        return Path(st["session_dir"]) if st is not None and st["session_dir"] else self.prob.work_path()

    @property
    def main_file(self) -> Path:
        return self.work_dir / cli.KIND_FILE.get(self.prob.kind, "solution.py")

    def side_width(self) -> int:
        return self.query_one("#side").size.width - 4

    # --- layout ------------------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="status")
        with Horizontal():
            with VerticalScroll(id="statement"):
                yield Markdown(self.prob.read("problem.md"), open_links=False)
            with TabbedContent(id="side", initial="tab-file"):
                with TabPane("My file", id="tab-file"):
                    with VerticalScroll():
                        yield Static(id="file", classes="pane")
                with TabPane("Hints", id="tab-hints"):
                    with VerticalScroll():
                        yield Markdown(id="hints", classes="pane", open_links=False)
                with TabPane("Check", id="tab-check"):
                    with VerticalScroll():
                        yield Static(id="check", classes="pane")
                with TabPane("Solution", id="tab-solution"):
                    with VerticalScroll():
                        yield Markdown(id="solution", classes="pane", open_links=False)
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = f"{self.prob.id}  {self.prob.title}"
        self.refresh_status()
        self.refresh_hints()
        last = self.work_dir / ".last_check.txt"
        self.query_one("#check", Static).update(
            Text.from_ansi(last.read_text(encoding="utf-8")) if last.exists()
            else Text("Not checked yet. Save your file, then press c.", style="dim")
        )
        self.query_one("#solution", Markdown).update(
            "*Hidden. Press **s** after a real attempt (at least one check).*"
        )
        self.refresh_file()
        self.set_interval(1.0, self.refresh_file)

    def refresh_status(self) -> None:
        st = self.state()
        hints = len(self.prob.hints())
        parts = [f"{self.prob.tier} · {self.prob.kind} · ~{self.prob.minutes} min"]
        if st is not None:
            status = "REVIEW" if st["is_review"] else st["status"]
            parts += [status, f"hints {st['hints_used']}/{hints}", f"failed checks {st['failed_checks']}"]
            if st["solution_viewed"]:
                parts.append("solution viewed")
        self.query_one("#status", Static).update("   ·   ".join(parts))

    def refresh_hints(self) -> None:
        st = self.state()
        hints = self.prob.hints()
        in_session = st is not None and (st["status"] == "started" or bool(st["is_review"]))
        shown = hints[: st["hints_used"]] if in_session else hints  # solved: all hints, like `learn hint`
        if not hints:
            text = "*This problem has no hints. The chapter is the best help: `learn read " + self.prob.module_id + "`.*"
        elif not shown:
            text = f"*No hints yet ({len(hints)} available). Press **h** when you have really tried.*"
        else:
            text = "\n\n".join(f"### Hint {i} of {len(hints)}\n\n{h}" for i, h in enumerate(shown, 1))
        self.query_one("#hints", Markdown).update(text)

    def refresh_file(self) -> None:
        path = self.main_file
        try:
            stat = path.stat()
            stamp = (stat.st_mtime, stat.st_size)
        except OSError:
            stamp = None
        if stamp == self._file_stamp:
            return
        self._file_stamp = stamp
        widget = self.query_one("#file", Static)
        if stamp is None:
            widget.update(Text(f"{cli.rel(path)} does not exist yet.", style="dim"))
            return
        lexer = "python" if path.suffix == ".py" else "markdown" if path.suffix == ".md" else "text"
        code = path.read_text(encoding="utf-8")
        header = Text(f"{cli.rel(path)}  (edit it in your editor; this view updates when you save)\n", style="dim")
        widget.update(Group(header, Syntax(code, lexer, line_numbers=True, word_wrap=True, theme="ansi_dark")))

    # --- actions -----------------------------------------------------------------------------

    def action_tab(self, tab: str) -> None:
        self.query_one(TabbedContent).active = tab

    def action_check(self) -> None:
        if self.busy:
            return
        if self.prob.kind == "explain" and runner.explain_word_count(self.main_file) >= cli.EXPLAIN_MIN_WORDS:
            def rated(rating: int | None) -> None:
                if rating:
                    self.start_check(rating)

            self.push_screen(RateScreen(self.prob.read("answer.md").strip()), rated)
        else:
            self.start_check(None)

    def start_check(self, rate: int | None) -> None:
        self.busy = True
        self.query_one("#check", Static).update(Text("Checking...", style="bold"))
        self.action_tab("tab-check")
        self.run_check(rate, self.side_width())

    @work(thread=True, exclusive=True)
    def run_check(self, rate: int | None, width: int) -> None:
        out, error = run_command(cli.cmd_check, width, problem=self.prob.id, rate=rate)
        self.call_from_thread(self.show_check, out, error)

    def show_check(self, out: str, error: str | None) -> None:
        self.busy = False
        for cli_words, key in (("(learn hint)", "(press h)"), ("learn solution", "s (solution)")):
            out = out.replace(cli_words, key)
        self.query_one("#check", Static).update(Text.from_ansi((out + (error or "")).rstrip() or "(no output)"))
        self.refresh_status()
        self.refresh_hints()
        st = self.state()
        if st is not None and st["status"] == "solved" and not st["is_review"] and "✓" in out:
            self.notify("Solved. Compare with the walkthrough (s), then q and learn next.", timeout=8)

    def action_hint(self) -> None:
        st = self.state()
        before = st["hints_used"] if st is not None else 0
        out, error = run_command(cli.cmd_hint, self.side_width(), problem=self.prob.id)
        self.refresh_hints()
        self.refresh_status()
        self.action_tab("tab-hints")
        st = self.state()
        if error or st is None or st["hints_used"] == before:
            self.notify(error or Text.from_ansi(out).plain.strip().splitlines()[0], timeout=5)

    def action_solution(self, confirmed: bool = False) -> None:
        st = self.state()
        solved = st is not None and st["status"] == "solved" and not st["is_review"]
        if not solved and not confirmed:
            # One key is easy to press by accident, so always ask while the problem is still open.
            tried = st is not None and st["failed_checks"] > 0
            first = ("Show the walkthrough now?" if tried
                     else "You have not checked an attempt yet (press c first).\nShow the walkthrough anyway?")

            def answer(yes: bool | None) -> None:
                if yes:
                    self.action_solution(confirmed=True)

            self.push_screen(ConfirmScreen(
                first + "\n\nIt counts as viewed: your score for this problem drops and it comes back for review sooner.",
                yes="Show it", no="Go back and try",
            ), answer)
            return
        # The learner confirmed above, which is what --force means on the command line.
        _, error = run_command(cli.cmd_solution, self.side_width(), problem=self.prob.id, force=True)
        if error:
            self.notify(error, timeout=6)
            return
        text = self.prob.read("solution.md").strip() or "*(no walkthrough written yet)*"
        mistakes = self.prob.read("mistakes.md").strip()
        if mistakes:
            text += "\n\n---\n\n## Common mistakes\n\n" + mistakes
        st = self.state()
        if st is not None and st["status"] != "solved":
            text += "\n\n---\n\n*Now close this tab (f), write it yourself from memory, and check again.*"
        self.query_one("#solution", Markdown).update(text)
        self.refresh_status()
        self.action_tab("tab-solution")

    def action_stuck(self) -> None:
        out, error = run_command(cli.cmd_stuck, self.side_width(), problem=self.prob.id)
        self.notify(error or Text.from_ansi(out).plain.strip(), timeout=8)

    def action_editor(self) -> None:
        if shutil.which("code") is None:
            self.notify(f"VS Code (`code`) not found. Open this file in your editor: {cli.rel(self.main_file)}", timeout=8)
            return
        cli.open_in_editor(self.work_dir / "problem.md", self.main_file)
        self.notify("Opened in VS Code. Save the file and this view updates.", timeout=4)


def run(problem_id: str) -> None:
    WorkspaceApp(problem_id).run()

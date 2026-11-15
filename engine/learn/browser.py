"""Full-screen syllabus browser (`learn syllabus` when `[ui] mode = "tui"`), built with Textual (optional extra `[tui]`).

Tracks and modules on the left, the highlighted module on the right with its problems underneath.
It only chooses; it returns a command as a list of words (`["read", "core.05"]`, `["work", "<problem id>"]`,
`["goto", "core.05"]`) that `cli._syllabus_browser` runs with the normal command code before reopening here.
"""

from __future__ import annotations

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Markdown, OptionList, Tree
from textual.widgets.option_list import Option

from learn import content, db, progress
from learn.syllabus import Module, Syllabus

ICON = {"mastered": "★", "in-progress": "◐", "not-started": "○", "no-content": "·"}


def module_markdown(m: Module, states: dict, status: str, solved: int, total: int) -> str:
    """The right-hand description of one module."""
    lines = [f"# {m.id}  {m.title}", ""]
    meta = f"{m.priority} · track {m.track} · {status}"
    if total:
        meta += f" · {solved}/{total} problems solved"
    lines += [f"*{meta}*", ""]
    if m.requires or m.requires_any:
        req = ", ".join(m.requires) + (f" (any of {', '.join(m.requires_any)})" if m.requires_any else "")
        lines += [f"*Suggested first: {req}*", ""]
    if m.chapter_path.exists():
        lines += ["**Chapter:** ready. Press **r** to read it.", ""]
    else:
        lines += ["**Chapter:** not written yet.", ""]
    lines += ["### Topics", ""] + [f"- {t}" for t in m.topics]
    lines += ["", "### You will be able to", ""] + [f"- {o}" for o in m.learning_outcomes]
    if m.project:
        lines += ["", f"**Project:** {m.project}"]
    if not total:
        lines += ["", f"*{m.planned_problems} problems planned; none written yet.*"]
    return "\n".join(lines)


def problem_label(p, state, today: str) -> Text:
    if state is None:
        icon, style = "○", "dim"
    elif state["status"] == "solved":
        due = state["review_due"] is not None and state["review_due"] <= today
        icon, style = ("↻", "yellow") if due else ("✓", "green")
    else:
        icon, style = "◐", "cyan"
    t = Text()
    t.append(f"{icon} ", style=style)
    t.append(f"{p.short:<5} {p.title}")
    kind = f"{p.tier}/{p.kind}" + (f" [{p.assessment}]" if p.assessment else "")
    t.append(f"  {kind}", style="dim")
    return t


class BrowserApp(App[list[str] | None]):
    TITLE = "learn syllabus"
    CSS = """
    #tree { width: 56; border-right: solid $primary-darken-2; }
    #detail { height: 1fr; padding: 0 2; }
    #problems { height: 45%; border-top: solid $primary-darken-2; }
    """
    BINDINGS = [
        Binding("r", "read", "Read chapter"),
        Binding("g", "goto", "Go here (set as current)"),
        Binding("p", "problems", "Problems"),
        Binding("m", "modules", "Modules"),
        Binding("q,escape", "quit_browser", "Quit"),
    ]

    def __init__(self, syl: Syllabus, states: dict, current: dict[str, str], focus: list[str],
                 track: str | None = None, module: str | None = None) -> None:
        super().__init__()
        self.syl, self.states, self.current, self.focus = syl, states, current, focus
        self.start_track, self.start_module = track, module
        self.selected: Module | None = None
        self.nodes: dict[str, object] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Tree("Syllabus", id="tree")
            with Vertical():
                with VerticalScroll(id="detail"):
                    yield Markdown(id="module", open_links=False)
                yield OptionList(id="problems")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "tracks and modules"
        tree = self.query_one("#tree", Tree)
        tree.show_root = False
        want_module = self.start_module or (self.current.get(self.start_track) if self.start_track else None)
        for t in self.syl.tracks:
            if self.start_track and t.id != self.start_track:
                continue
            opened = t.id in self.focus or t.id == self.start_track
            branch = tree.root.add(f"{t.title}", data=t.id, expand=opened)
            for m in t.modules:
                mp = progress.module_progress(m.id, self.states)
                label = Text()
                label.append(f"{ICON[mp.status]} ", style="cyan" if mp.status != "no-content" else "dim")
                label.append(f"{m.id:<8}")
                # a fixed-width count right after the id, so long titles can never push it off the screen
                count = f"{mp.solved}/{mp.total}" if mp.total else ("chap" if m.chapter_path.exists() else "")
                label.append(f" {count:>6}  ", style="dim")
                label.append(m.title)
                if self.current.get(t.id) == m.id and t.id in self.focus:
                    label.append("  ← you are here", style="bold yellow")
                leaf = branch.add_leaf(label, data=m.id)
                self.nodes[m.id] = leaf
                if want_module is None and self.current.get(t.id) == m.id and t.id in self.focus:
                    want_module = m.id  # first focus track's current module
        tree.focus()
        if want_module and want_module in self.nodes:
            self.nodes[want_module].parent.expand()
            self.show(want_module)
            self.call_after_refresh(self.place_cursor, want_module)  # the tree lines exist only after the first layout

    def place_cursor(self, module_id: str) -> None:
        self.query_one("#tree", Tree).move_cursor(self.nodes[module_id])

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        data = event.node.data
        if data in self.nodes:
            self.show(data)

    def show(self, module_id: str) -> None:
        m = self.syl.module(module_id)
        self.selected = m
        mp = progress.module_progress(m.id, self.states)
        self.query_one("#module", Markdown).update(module_markdown(m, self.states, mp.status, mp.solved, mp.total))
        problems = self.query_one("#problems", OptionList)
        problems.clear_options()
        today = db.today()
        probs = content.problems_for_module(m.id)
        problems.add_options([Option(problem_label(p, self.states.get(p.id), today), id=p.id) for p in probs])
        if probs:
            problems.highlighted = 0  # so Tab then Enter opens the first problem without pressing Down
        problems.border_title = (f"Problems ({len(probs)}): p to focus, Enter opens one"
                                 if probs else "No problems written yet")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(["work", event.option.id])

    def action_read(self) -> None:
        if self.selected is None:
            return
        if not self.selected.chapter_path.exists():
            self.notify(f"The chapter for {self.selected.id} is not written yet.", timeout=4)
            return
        self.exit(["read", self.selected.id])

    def action_goto(self) -> None:
        if self.selected is not None:
            self.exit(["goto", self.selected.id])

    def action_problems(self) -> None:
        self.query_one("#problems", OptionList).focus()

    def action_modules(self) -> None:
        self.query_one("#tree", Tree).focus()

    def action_quit_browser(self) -> None:
        self.exit(None)


def run(syl: Syllabus, states: dict, current: dict[str, str], focus: list[str],
        track: str | None = None, module: str | None = None) -> list[str] | None:
    return BrowserApp(syl, states, current, focus, track, module).run()

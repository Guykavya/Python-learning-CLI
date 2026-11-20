"""Full-screen home (plain `learn` when `[ui] mode = "tui"`), built with Textual (optional extra `[tui]`).

It only chooses what to do next and returns the command as a list of words (like `["next"]`);
`cli._tui_menu` runs it with the normal command code and reopens the home afterwards, so scoring and
progress rules stay in `cli.py`. The data comes in as plain values from `cli._home_data`.
"""

from __future__ import annotations

import time
from datetime import datetime

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.suggester import SuggestFromList
from textual.widgets import Footer, Header, Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from learn import scene, ui

TAGS = {"review": ("Review", "yellow"), "new": ("New", "cyan"), "external": ("Site", "magenta")}


def actions(data: dict) -> list[tuple[str, str, list[str] | None]]:
    """(key, label, command words). `None` as the words means: ask for a problem id first."""
    working = data["working"]
    rows: list[tuple[str, str, list[str] | None]] = []
    if working:
        tag = "[REVIEW] " if working["review"] else ""
        rows.append(("c", f"Continue  {tag}{working['id']}  {working['title']}", ["work"]))
    rows.append(("n", "Start learning" if data["fresh"] else "Start next problem", ["next"]))
    rows += [
        ("r", "Read the book (all chapters)", ["read"]),
        ("s", "Syllabus browser", ["syllabus"]),
        ("t", "Stats", ["stats"]),
        ("p", "Today's plan (printed)", ["today"]),
        ("i", "Start a problem by id", None),
        ("x", "Start over (erase progress)", ["reset"]),
    ]
    return rows


def bar(score: float, width: int = 16) -> str:
    filled = max(0, min(width, round(score * width)))
    return "█" * filled + "░" * (width - filled)


def logo(data: dict, frame: int = -1) -> Text:
    """The PYTHON banner in the Python logo colours, what this app is, and who it belongs to."""
    return scene.logo_text(ui.BANNER, ui.CAPTION, data.get("name", ""), frame)


def overview(data: dict) -> Text:
    """The right-hand panel: the day, today's plan, and where you are in each focus track."""
    t = Text()
    t.append(f"Day {data['day']}", style="bold")
    t.append(f"  ·  {data['date']}  ·  {data['minutes']} min plan\n", style="dim")
    if data["working"]:
        w = data["working"]
        t.append("Working on  ", style="dim")
        if w["review"]:
            t.append("[REVIEW] ", style="yellow")
        t.append(w["id"], style="bold")
        t.append(f"  {w['title']}\n")
    if data["due"]:
        t.append(f"{data['due']} review(s) due\n", style="yellow")

    t.append("\nToday's plan\n", style="bold cyan")
    if not data["plan"]:
        t.append("  Nothing planned. Every problem in your focus tracks is solved, or none is due.\n", style="dim")
    total = 0
    for item in data["plan"]:
        tag, color = TAGS.get(item["kind"], (item["kind"], "white"))
        t.append(f"  {item['n']}. ")
        t.append(f"[{tag}] ", style=color)
        t.append(item["label"] + "\n")
        t.append(f"       ~{item['minutes']} min · {item['reason']}\n", style="dim")
        total += item["minutes"]
    if data["plan"]:
        t.append(f"\n  About {total} minutes.\n", style="dim")

    t.append("\nWhere you are\n", style="bold cyan")
    for tr in data["tracks"]:
        t.append(f"  {tr['track']:<6}", style="bold")
        t.append(f" {tr['module']:<9} {tr['title']}\n")
        count = f"{tr['solved']}/{tr['total']} solved" if tr["total"] else "no problems written yet"
        t.append(f"         {bar(tr['score']) if tr['total'] else ''} {count}\n", style="dim")
    return t


class IdScreen(ModalScreen["str | None"]):
    """Ask for a problem id. Type a few letters; the right-arrow key accepts the grey suggestion."""

    CSS = """
    IdScreen { align: center middle; }
    #box { width: 70; height: auto; border: thick $primary; background: $surface; padding: 1 2; }
    """
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, ids: list[str]) -> None:
        super().__init__()
        self.ids = set(ids)
        self.suggestions = ids

    def compose(self) -> ComposeResult:
        with Vertical(id="box"):
            yield Label("Problem id, for example core.01.p003  (Enter to start, Esc to cancel)")
            yield Input(placeholder="core.01.p003", suggester=SuggestFromList(self.suggestions), id="id")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if value in self.ids:
            self.dismiss(value)
        else:
            self.notify(f"No problem called '{value}'.", severity="error", timeout=4)

    def action_cancel(self) -> None:
        self.dismiss(None)


class HomeApp(App[list[str] | None]):
    TITLE = "learn"
    CSS = """
    #left { width: 46; border-right: solid $primary-darken-2; }
    #logo { height: auto; padding: 1 1 1 1; }
    #menu { height: auto; }
    #rain-left { height: 1fr; padding: 1 1 0 1; }
    #right { padding: 0 2; }
    #top { height: 1fr; }
    #main { width: 1fr; }
    #info { height: auto; max-height: 60%; }
    #rain-right { height: 1fr; padding: 1 0 0 0; }
    #side { width: 64; align-horizontal: right; }
    #clockbox { width: auto; height: auto; border: round #4B8BBE; padding: 0 2; }
    #hello { width: auto; height: auto; text-style: bold; }
    #clock { width: auto; height: auto; padding: 1 0 0 0; }
    #poem { height: 1fr; padding: 1 0 0 1; }
    """
    BINDINGS = [Binding("q,escape", "quit_home", "Quit")]

    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data
        self.rows = actions(data)
        for key, label, _ in self.rows:
            self.bind(key, f"pick('{key}')", description=label, show=False)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="left"):
                yield Static(logo(self.data), id="logo")
                yield OptionList(
                    *(Option(f"{key}  {label}", id=key) for key, label, _ in self.rows),
                    id="menu",
                )
                yield Static(id="rain-left")
            with Vertical(id="right"):
                with Horizontal(id="top"):
                    with Vertical(id="main"):
                        with VerticalScroll(id="info"):
                            yield Static(overview(self.data), id="overview")
                        yield Static(id="rain-right")
                    with Vertical(id="side"):
                        now = datetime.now()
                        with Vertical(id="clockbox"):  # remove this border in the CSS above for a bare clock
                            yield Static(scene.greeting(now.hour, self.data.get("name", "")), id="hello")
                            yield Static(scene.clock_text(now), id="clock")
                        yield Static(id="poem")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "home"
        menu = self.query_one("#menu", OptionList)
        menu.focus()
        menu.highlighted = 0
        self.rain_left, self.rain_right, self.poem = scene.Rain(seed=1), scene.Rain(seed=2), scene.Poem()
        self.colon = True
        self.shimmering = False
        if self.data.get("animations", True):
            self.set_interval(1 / scene.FPS, self.tick)
        else:
            for widget in ("#rain-left", "#rain-right", "#poem"):
                self.query_one(widget).display = False

    def tick(self) -> None:
        """One animation frame, safe to call at any moment: while the screen is still being built or is being
        torn down (quitting) the widgets do not exist, and a timer must never crash the app over that."""
        try:
            self.draw_frame()
        except NoMatches:
            pass

    def draw_frame(self) -> None:
        """The rain, the poem, the logo shimmer and the clock's blinking colon."""
        for rain, widget in ((self.rain_left, "#rain-left"), (self.rain_right, "#rain-right")):
            stage = self.query_one(widget, Static)
            rain.resize(stage.content_size.width, stage.content_size.height)
            rain.step()
            stage.update(rain.render())
        narrow = self.size.width < 120  # too little room beside the plan: keep the clock, drop the poem
        self.query_one("#poem").display = not narrow
        self.query_one("#side").styles.width = 30 if narrow else 64
        poem = self.query_one("#poem", Static)
        self.poem.step()
        if not narrow:
            poem.update(self.poem.render(poem.content_size.width, poem.content_size.height))
        frame = self.poem.frame
        shimmer = scene.shimmer_pos(frame, 43, 5) is not None
        if shimmer or self.shimmering:  # redraw while it sweeps, and once more when it rests
            self.query_one("#logo", Static).update(logo(self.data, frame))
        self.shimmering = shimmer
        colon = int(time.time()) % 2 == 0
        if colon != self.colon:
            self.colon = colon
            self.query_one("#clock", Static).update(scene.clock_text(datetime.now(), colon))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.pick(event.option.id)

    def action_pick(self, key: str) -> None:
        self.pick(key)

    def pick(self, key: str) -> None:
        words = next(w for k, _, w in self.rows if k == key)
        if words is None:
            def got(problem_id: str | None) -> None:
                if problem_id:
                    self.exit(["start", problem_id])

            self.push_screen(IdScreen(self.data["problem_ids"]), got)
        else:
            self.exit(list(words))

    def action_quit_home(self) -> None:
        self.exit(None)


def run(data: dict) -> list[str] | None:
    return HomeApp(data).run()

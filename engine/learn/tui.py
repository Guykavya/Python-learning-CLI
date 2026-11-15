"""Optional full-screen chapter reader built with Textual (`learn read <module> --tui`).

The plain reader in `reader.py` stays the default and the fallback: this module is only imported
when the learner asks for `--tui`, and `textual` is an optional extra (`pip install -e ".[tui]"`).
It reuses `reader.split_sections` and `reader._prepare`, so sections, hidden answers and page
anchors behave exactly as in the plain reader.
"""

from __future__ import annotations

from collections.abc import Callable

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Footer, Header, Markdown, OptionList
from textual.widgets.option_list import Option

from learn import reader


class ReaderApp(App[None]):
    """Contents on the left, one `## ` section on the right."""

    TITLE = "learn"
    CSS = """
    #contents { width: 34; border-right: solid $primary-darken-2; }
    #contents.hidden { display: none; }
    #page { padding: 0 2; }
    #page Markdown { max-width: 100; }
    """
    BINDINGS = [
        Binding("n,right", "next", "Next"),
        Binding("p,left", "previous", "Previous"),
        Binding("a", "answers", "Answers"),
        Binding("c", "contents", "Contents"),
        Binding("space", "page_down", "Page down", show=False),
        Binding("b", "page_up", "Page up", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, title: str, text: str, start: int, save: Callable[[int], None]) -> None:
        super().__init__()
        self.chapter_title = title
        self.sections = reader.split_sections(text)
        self.index = max(0, min(start, len(self.sections) - 1))
        self.reveal = False
        self.save = save
        self.finished = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield OptionList(
                # Section titles already carry their chapter number ("4. Slicing"), so show them as they are.
                *(Option(s.title, id=str(i)) for i, s in enumerate(self.sections)),
                id="contents",
            )
            with VerticalScroll(id="page"):
                yield Markdown(id="text", open_links=False)
        yield Footer()

    def on_mount(self) -> None:
        self.show(self.index)

    # --- showing a section -------------------------------------------------------------------

    def show(self, index: int, reveal: bool = False) -> None:
        self.index, self.reveal = index, reveal
        section = self.sections[index]
        self.save(index)
        self.sub_title = f"{self.chapter_title}  ·  section {index + 1} of {len(self.sections)}"
        lines = reader._prepare(section.lines, reveal)
        if reader.has_answers(section.lines) and not reveal:
            lines += ["", "---", "*Press **a** to show the answers in this section.*"]
        self.query_one("#text", Markdown).update("\n".join(lines))
        self.query_one("#page", VerticalScroll).scroll_home(animate=False)
        contents = self.query_one("#contents", OptionList)
        contents.highlighted = index

    def section_source(self) -> str:
        """The Markdown currently on screen (used by the tests)."""
        return self.query_one("#text", Markdown).source

    # --- actions -----------------------------------------------------------------------------

    def action_next(self) -> None:
        if self.index + 1 < len(self.sections):
            self.show(self.index + 1)
        elif not self.finished:
            self.finished = True
            self.notify("Chapter finished. Practise it with: learn next", timeout=6)

    def action_previous(self) -> None:
        if self.index > 0:
            self.show(self.index - 1)

    def action_answers(self) -> None:
        if reader.has_answers(self.sections[self.index].lines):
            self.show(self.index, reveal=not self.reveal)
        else:
            self.notify("This section has no hidden answers.", timeout=3)

    def action_contents(self) -> None:
        self.query_one("#contents", OptionList).toggle_class("hidden")

    def action_page_down(self) -> None:
        self.query_one("#page", VerticalScroll).scroll_page_down()

    def action_page_up(self) -> None:
        self.query_one("#page", VerticalScroll).scroll_page_up()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.show(int(event.option.id))
        self.query_one("#page", VerticalScroll).focus()


def read_chapter(title: str, text: str, start: int, save: Callable[[int], None]) -> None:
    ReaderApp(title, text, start, save).run()

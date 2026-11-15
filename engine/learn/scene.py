"""The living decoration of the full-screen home: code rain, the Zen of Python typed out line by line,
a shimmering logo and a block clock.

Pure logic: every function returns a Rich `Text`, and `Scene.step()` advances one animation frame.
No Textual here, so it is easy to test; `home.py` calls it from a timer. Only plain characters are used
(block, box-drawing and circle glyphs), which Windows Terminal draws fine.
"""

from __future__ import annotations

import codecs
import contextlib
import functools
import io
import keyword
import math
import random
import textwrap
from datetime import datetime

from rich.text import Text

BLUE, DEEP, YELLOW, RED = "#4B8BBE", "#306998", "#FFD43B", "#E5534B"  # the Python logo's colours
TAIL_1, TAIL_2 = "#2F5373", "#1D3347"
FPS = 12
MAX_WIDTH, MAX_HEIGHT = 110, 30  # a huge terminal must not mean a slow frame

WORDS = sorted(
    {w for w in keyword.kwlist if w not in ("True", "False", "None")}
    | {"print", "len", "range", "self", "dict", "list", "set", "str", "int", "open", "zip", "map", "type",
       "super", "enumerate", "sorted"}
)


@functools.cache
def _poem_text() -> list[str]:
    with contextlib.redirect_stdout(io.StringIO()):  # importing `this` prints the poem once
        import this
    return [line for line in codecs.decode(this.s, "rot13").splitlines() if line.strip()]


def zen_lines() -> tuple[str, ...]:
    """The 19 aphorisms of `import this`, taken from Python itself (so no wording is retyped by hand)."""
    return tuple(_poem_text()[1:])


def poem_lines() -> tuple[str, ...]:
    """What a Python prompt shows for `import this`: the command, the title, then the 19 aphorisms."""
    return (">>> import this", *_poem_text())


class Rain:
    """Slow falling Python keywords, spelled downwards, with a bright yellow head and a fading blue tail."""

    def __init__(self, width: int = 40, height: int = 20, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.w, self.h = width, height
        self.frame = 0
        self.warm = False  # becomes True once the area has been pre-filled with rain
        self.drops: list[list] = []  # [column, head row, speed, word, length]

    def _spawn(self, row: float | None = None) -> None:
        length = self.rng.randint(5, 11)
        self.drops.append([self.rng.randrange(0, self.w, 2), -float(length) if row is None else row,
                           self.rng.uniform(0.25, 0.6), self.rng.choice(WORDS), length])

    def resize(self, width: int, height: int) -> None:
        self.w, self.h = max(0, min(width, MAX_WIDTH)), max(0, min(height, MAX_HEIGHT))

    def step(self) -> None:
        self.frame += 1
        if self.w < 10 or self.h < 3:
            self.drops.clear()
            return
        if not self.warm:  # start with rain already falling everywhere, not an empty screen that fills slowly
            self.warm = True
            for _ in range(self.w // 6):
                self._spawn(self.rng.uniform(0, self.h + 6))
        if len(self.drops) < self.w // 4 and self.rng.random() < 0.35:
            self._spawn()
        for d in self.drops:
            d[1] += d[2]
        self.drops = [d for d in self.drops if d[1] - d[4] <= self.h]

    def render(self) -> Text:
        w, h = self.w, self.h
        if w < 10 or h < 3:
            return Text("")
        chars = [[" "] * w for _ in range(h)]
        styles = [[""] * w for _ in range(h)]
        for x, y, _, word, length in self.drops:
            head = int(y)
            for k in range(length):  # k = 0 is the bright head; the word reads downwards and ends at the head
                row = head - k
                if 0 <= row < h and 0 <= x < w:
                    chars[row][x] = word[(len(word) - 1 - k) % len(word)]
                    styles[row][x] = ("bold " + YELLOW if k == 0 else BLUE if k <= 2
                                      else TAIL_1 if k <= length // 2 else TAIL_2)
        out = Text(no_wrap=True, overflow="crop")
        for y in range(h):
            run: list[str] = []
            style = styles[y][0]
            for x in range(w):
                if styles[y][x] != style:
                    out.append("".join(run), style=style or None)
                    run, style = [], styles[y][x]
                run.append(chars[y][x])
            out.append("".join(run), style=style or None)
            if y < h - 1:
                out.append("\n")
        return out


class Poem:
    """`>>> import this`, then every aphorism typed on the line below the previous one. When the last one
    is done it stays for a while, then the whole screen is wiped and it starts again from the prompt."""

    TYPE_SPEED = 2.0  # characters per frame
    PAUSE = 9         # frames between two lines
    HOLD = FPS * 7    # frames the finished poem stays

    def __init__(self, lines: tuple[str, ...] | list[str] | None = None) -> None:
        self.lines = list(lines or poem_lines())
        self.frame = 0
        self.reset()

    def reset(self) -> None:
        self.idx, self.shown, self.phase, self.wait = 0, 0.0, "typing", 0

    @property
    def finished(self) -> bool:
        return self.phase == "hold"

    def step(self) -> None:
        self.frame += 1
        if self.phase == "typing":
            self.shown += self.TYPE_SPEED
            if self.shown >= len(self.lines[self.idx]):
                self.shown, self.phase, self.wait = float(len(self.lines[self.idx])), "pause", self.PAUSE
        elif self.phase == "pause":
            self.wait -= 1
            if self.wait <= 0:
                self.idx += 1
                self.shown = 0.0
                self.phase, self.wait = ("hold", self.HOLD) if self.idx >= len(self.lines) else ("typing", 0)
        else:  # hold
            self.wait -= 1
            if self.wait <= 0:
                self.reset()  # wipe and begin again

    def render(self, width: int, height: int) -> Text:
        """The lines typed so far. A poem taller than the pane scrolls: the newest rows stay in view."""
        if width < 10 or height < 1:
            return Text("")
        rows: list[tuple[str, str]] = []
        for i in range(min(self.idx + 1, len(self.lines))):
            # wrap the full line first, so words never jump between rows while the line is being typed
            full = textwrap.wrap(self.lines[i], width - 2) or [""]
            if i < self.idx:
                parts = full
            else:
                budget, parts = int(self.shown), []
                for part in full:
                    parts.append(part[:max(0, budget)])
                    budget -= len(part)
                parts = [p for p in parts if p] or [""]
            style = BLUE if i == 0 else f"bold {YELLOW}" if i == 1 else ""
            rows += [(p, style) for p in parts]
        rows = rows[-height:]
        out = Text(no_wrap=True, overflow="crop")
        for n, (part, style) in enumerate(rows):
            out.append(part, style=style or None)
            if n == len(rows) - 1 and self.phase != "hold" and (self.frame // 6) % 2 == 0:
                out.append("▌", style=YELLOW)  # blinking caret at the end of the newest line
            if n < len(rows) - 1:
                out.append("\n")
        return out


# --- the logo, the greeting and the clock ------------------------------------------------------

def shimmer_pos(frame: int, width: int, height: int) -> float | None:
    """Where the light band is on the logo (None while it rests): a sweep of 3 s every 8 s."""
    f = frame % (FPS * 8)
    if f >= FPS * 3:
        return None
    return f / (FPS * 3) * (width + 2 * height + 8) - 4


def logo_text(banner: list[str], caption: str, name: str = "", frame: int = -1) -> Text:
    """The PYTHON banner (blue top, yellow bottom), a white shimmer sweeping across it, caption and name."""
    pos = shimmer_pos(frame, max(len(line) for line in banner), len(banner)) if frame >= 0 else None
    t = Text(no_wrap=True)
    for y, line in enumerate(banner):
        base = BLUE if y < 3 else YELLOW
        for x, ch in enumerate(line):
            hot = pos is not None and ch != " " and abs((x + 2 * y) - pos) <= 2.5
            t.append(ch, style="bold #FFFFFF" if hot else f"bold {base}")
        t.append("\n")
    t.append(caption, style="dim")
    if name:
        t.append(f"\nby {name}", style="bold")
    return t


def greeting(hour: int, name: str = "") -> str:
    who = f", {name}" if name else ""
    if 5 <= hour < 12:
        return f"Good morning{who}"
    if 12 <= hour < 17:
        return f"Good afternoon{who}"
    if 17 <= hour < 22:
        return f"Good evening{who}"
    return f"Still up{who}?"


DIGITS = {
    "0": ("███", "█ █", "█ █", "█ █", "███"),
    "1": (" ██", "  █", "  █", "  █", "  █"),
    "2": ("███", "  █", "███", "█  ", "███"),
    "3": ("███", "  █", "███", "  █", "███"),
    "4": ("█ █", "█ █", "███", "  █", "  █"),
    "5": ("███", "█  ", "███", "  █", "███"),
    "6": ("███", "█  ", "███", "█ █", "███"),
    "7": ("███", "  █", "  █", "  █", "  █"),
    "8": ("███", "█ █", "███", "█ █", "███"),
    "9": ("███", "█ █", "███", "  █", "███"),
}


def clock_text(now: datetime, colon: bool = True) -> Text:
    """HH:MM in 3x5 block digits. The colon blinks once a second."""
    rows = [""] * 5
    for ch in now.strftime("%H:%M"):
        glyph = DIGITS[ch] if ch != ":" else (" ", "█" if colon else " ", " ", "█" if colon else " ", " ")
        rows = [r + g + " " for r, g in zip(rows, glyph)]
    return Text("\n".join(r.rstrip() for r in rows), style=f"bold {BLUE}", no_wrap=True)

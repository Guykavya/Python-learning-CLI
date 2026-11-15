"""The home screen's decoration: Zen typewriter, snake, code rain, shimmer, greeting, clock. Pure logic, no Textual."""

from datetime import datetime

from learn import scene, ui


def plain(text) -> str:
    return text.plain


def test_zen_lines_come_from_python_itself():
    lines = scene.zen_lines()
    assert len(lines) == 19, "the Zen of Python has 19 aphorisms"
    assert lines[0] == "Beautiful is better than ugly."
    assert "Namespaces are one honking great idea -- let's do more of those!" in lines


def test_poem_starts_with_the_prompt_then_the_title_then_all_aphorisms():
    lines = scene.poem_lines()
    assert lines[0] == ">>> import this", "it looks like a Python prompt"
    assert lines[1] == "The Zen of Python, by Tim Peters", "the title comes from Python itself"
    assert len(lines) == 2 + 19


def test_poem_types_each_line_below_the_previous_one():
    p = scene.Poem(["first line", "second line", "third line"])
    p.step()
    assert "first line" not in p.render(40, 10).plain, "a line must not appear all at once"
    seen = []
    for _ in range(400):
        p.step()
        if p.phase == "hold":
            break
    assert p.phase == "hold", "the poem must finish"
    assert p.render(40, 10).plain.split("\n") == ["first line", "second line", "third line"], \
        "lines stay on screen, each one below the previous"


def test_poem_wipes_and_starts_again_after_the_hold():
    p = scene.Poem(["first line", "second line"])
    for _ in range(400):
        p.step()
        if p.phase == "hold":
            break
    for _ in range(p.HOLD + 1):
        p.step()
    assert (p.idx, p.phase) == (0, "typing"), "after the hold it starts again from the first line"
    assert "second line" not in p.render(40, 10).plain, "the old lines are wiped, not kept"


def test_poem_scrolls_so_the_newest_line_stays_visible():
    p = scene.Poem([f"line {i}" for i in range(20)])
    for _ in range(2000):
        p.step()
        if p.phase == "hold":
            break
    rows = p.render(30, 5).plain.split("\n")
    assert len(rows) == 5 and rows[-1] == "line 19", "a pane shorter than the poem shows the newest rows"


def test_poem_wraps_long_lines_to_the_pane_width():
    p = scene.Poem(["word " * 30])
    for _ in range(400):
        p.step()
        if p.phase == "hold":
            break
    rows = p.render(40, 20).plain.split("\n")
    assert len(rows) > 1 and all(len(r) <= 40 for r in rows), "long aphorisms wrap inside the pane"


def test_rain_renders_exact_size_and_never_overflows():
    for w, h in ((20, 6), (44, 30), (110, 30)):
        r = scene.Rain(w, h, seed=4)
        for _ in range(60):
            r.step()
        rows = r.render().plain.split("\n")
        assert len(rows) == h and all(len(row) == w for row in rows), "every frame fills exactly width x height"


def test_rain_is_already_falling_on_the_first_frame():
    r = scene.Rain(44, 30, seed=8)
    r.step()
    assert r.render().plain.strip(), "the home must open with rain on screen, not an empty area that fills slowly"


def test_tiny_or_zero_area_renders_nothing_instead_of_crashing():
    r = scene.Rain(5, 2)
    r.step()
    assert r.render().plain == ""
    r.resize(0, 0)
    r.step()
    assert r.render().plain == ""
    assert scene.Poem().render(5, 0).plain == ""


def test_resize_is_capped_so_a_huge_terminal_stays_fast():
    r = scene.Rain()
    r.resize(500, 200)
    assert (r.w, r.h) == (scene.MAX_WIDTH, scene.MAX_HEIGHT)


def test_rain_falls_and_is_cleaned_up():
    r = scene.Rain(60, 20, seed=6)
    for _ in range(200):
        r.step()
    assert 0 < len(r.drops) <= 60 // 4, "some rain, but never more than a quarter of the columns"
    assert all(d[1] - d[4] <= 20 for d in r.drops), "drops that fell off the bottom must be removed"
    assert any(word in r.render().plain for word in ("e", "f", "i")), "the rain spells letters of Python keywords"


def test_shimmer_sweeps_then_rests():
    positions = [scene.shimmer_pos(f, 43, 5) for f in range(scene.FPS * 8)]
    assert positions[0] is not None and positions[-1] is None, "it sweeps first, then rests"
    assert positions[10] > positions[1], "the band moves to the right"
    hot = scene.logo_text(ui.BANNER, "cap", "", frame=scene.FPS)  # mid-sweep
    assert any("#FFFFFF" in str(span.style) for span in hot.spans), "a white band must cross the logo"
    rest = scene.logo_text(ui.BANNER, "cap", "", frame=scene.FPS * 5)
    assert not any("#FFFFFF" in str(span.style) for span in rest.spans), "no band while resting"


def test_logo_keeps_python_colours_and_the_name():
    t = scene.logo_text(ui.BANNER, ui.CAPTION, "Asha")
    assert "by Asha" in t.plain and ui.CAPTION in t.plain
    assert any(scene.BLUE in str(s.style) for s in t.spans) and any(scene.YELLOW in str(s.style) for s in t.spans)
    assert "by " not in scene.logo_text(ui.BANNER, ui.CAPTION, "").plain, "no name set, no credit line"


def test_greeting_follows_the_hour_and_the_name():
    assert scene.greeting(8, "Asha") == "Good morning, Asha"
    assert scene.greeting(14, "Asha") == "Good afternoon, Asha"
    assert scene.greeting(19, "Asha") == "Good evening, Asha"
    assert scene.greeting(23, "Asha") == "Still up, Asha?"
    assert scene.greeting(3) == "Still up?", "no name set: no comma and no name"
    assert scene.greeting(9) == "Good morning"


def test_clock_draws_five_rows_and_the_colon_blinks():
    now = datetime(2026, 11, 15, 21, 44)
    on, off = scene.clock_text(now, True), scene.clock_text(now, False)
    assert len(on.plain.split("\n")) == 5, "block digits are five rows tall"
    assert on.plain != off.plain, "the colon must disappear on the off beat"
    assert scene.clock_text(datetime(2026, 1, 1, 0, 0)).plain.count("█") > 20

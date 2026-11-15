"""[ui] mode switch, and the full-screen home and syllabus browser (optional Textual extra)."""

import asyncio

import pytest

from learn import cli, content, db

textual = pytest.importorskip("textual", reason="optional extra: pip install -e '.[tui]'")

PID = "core.02.p001"


async def wait_until(pilot, condition, what: str, seconds: float = 20.0) -> None:
    """Poll instead of sleeping a fixed time: CI machines (Windows, macOS) can be much slower than a laptop."""
    waited = 0.0
    while not condition():
        assert waited < seconds, f"timed out after {seconds}s waiting for: {what}"
        await pilot.pause(0.1)
        waited += 0.1


@pytest.fixture
def tty(monkeypatch):
    """Pretend a real terminal is attached (pytest runs without one)."""
    monkeypatch.setattr(cli, "_is_terminal", lambda: True)
    monkeypatch.setattr(cli, "_force_plain", False)
    monkeypatch.delenv("LEARN_UI", raising=False)


def test_default_mode_is_plain(home, tty):
    assert cli.ui_mode() == "plain", "tui must be opt-in"


def test_mode_needs_setting_terminal_and_textual(home, tty, monkeypatch):
    monkeypatch.setenv("LEARN_UI", "tui")
    assert cli.ui_mode() == "tui"
    monkeypatch.setattr(cli, "_is_terminal", lambda: False)
    assert cli.ui_mode() == "plain", "a pipe or a script must always get plain output"
    monkeypatch.setattr(cli, "_is_terminal", lambda: True)
    monkeypatch.setattr(cli.importlib.util, "find_spec", lambda name: None)
    assert cli.ui_mode() == "plain", "without Textual the run must stay plain, not crash"


def test_config_setting_turns_tui_on_and_plain_flag_beats_it(home, tty):
    cli.main(["config", "set", "ui.mode", "tui"])
    assert cli.ui_mode() == "tui", "config.toml [ui] mode = tui must be honoured"
    cli._force_plain = True
    assert cli.ui_mode() == "plain", "--plain must win for one run"


def test_start_opens_workspace_in_tui_mode_and_prints_in_plain(home, tty, monkeypatch, capsys):
    from learn import workspace

    opened = []
    monkeypatch.setattr(workspace, "run", opened.append)
    monkeypatch.setenv("LEARN_UI", "tui")
    cli.main(["init"])
    capsys.readouterr()
    assert cli.main(["start", PID]) == 0
    assert opened == [PID], "in tui mode, learn start must open the workspace"
    assert db.problem_state(db.connect(), PID)["status"] == "started", "the workspace path must still start the problem"
    assert content.get(PID).title not in capsys.readouterr().out, "no printed statement behind the full screen"

    opened.clear()
    assert cli.main(["--plain", "start", PID]) == 0
    assert opened == [] and content.get(PID).title in capsys.readouterr().out, "--plain keeps the printed statement"


def test_tui_menu_runs_the_chosen_command_then_reopens(home, tty, monkeypatch):
    from learn import home as home_screen

    cli.main(["init"])
    answers = iter([["stats"], ["next"], None])
    monkeypatch.setattr(home_screen, "run", lambda data: next(answers))
    calls = []
    monkeypatch.setattr(cli, "_run_argv", lambda argv, pause=False: calls.append((argv, pause)))
    cli._tui_menu()
    assert calls == [(["stats"], True), (["next"], False)], "printing commands pause so their output is not wiped"


def test_home_screen_returns_the_chosen_command(home):
    from learn.home import HomeApp

    cli.main(["init"])
    data = cli._home_data()
    assert data["fresh"] and data["plan"], "a new learner sees a plan"

    async def drive() -> None:
        app = HomeApp(data)
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            await pilot.press("n")
            await pilot.pause()
        assert app.return_value == ["next"], "n must start the next problem"

        app = HomeApp(data)
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            await pilot.press("i")
            await pilot.pause()
            await pilot.press(*PID, "enter")
            await pilot.pause()
        assert app.return_value == ["start", PID], "i then a valid id must start that problem"

        app = HomeApp(data)
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            await pilot.press("q")
            await pilot.pause()
        assert app.return_value is None, "q must leave"

    asyncio.run(drive())


def test_home_shows_the_logo_and_the_configured_name(home):
    from learn.home import HomeApp

    cli.main(["init"])
    assert cli._home_data()["name"] == "", "no name unless the learner sets one (the course is shared)"
    cli.main(["config", "set", "ui.name", "Asha"])
    data = cli._home_data()
    assert data["name"] == "Asha"

    async def drive() -> None:
        app = HomeApp(data)
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            logo = str(app.query_one("#logo").content)
            assert "by Asha" in logo and "Python learning module" in logo, "the logo must say what the app is and who made it"
            assert "Asha" in str(app.query_one("#hello").content), "the greeting uses the name from [ui] name"

    asyncio.run(drive())


def test_home_offers_continue_when_a_problem_is_open(home):
    from learn.home import actions

    cli.main(["init"])
    cli.main(["--plain", "start", PID])
    rows = actions(cli._home_data())
    assert rows[0][0] == "c" and rows[0][2] == ["work"], "an unfinished problem is offered first"


def test_browser_reads_a_chapter_and_opens_a_problem(home):
    from learn.browser import BrowserApp
    from learn.syllabus import load

    cli.main(["init"])
    syl = load()
    conn = db.connect()
    states = db.states(conn)

    async def drive() -> None:
        app = BrowserApp(syl, states, {"core": "core.02"}, ["core"], module="core.02")
        async with app.run_test(size=(150, 45)) as pilot:
            await pilot.pause()
            assert app.selected.id == "core.02", "the browser must open on the requested module"
            await pilot.press("r")
            await pilot.pause()
        assert app.return_value == ["read", "core.02"], "r must read the highlighted module's chapter"

        app = BrowserApp(syl, states, {"core": "core.02"}, ["core"], module="core.02")
        async with app.run_test(size=(150, 45)) as pilot:
            await pilot.pause()
            await pilot.press("p", "enter")
            await pilot.pause()
        assert app.return_value[0] == "work" and app.return_value[1].startswith("core.02.p"), \
            "Enter on a problem must open it in the workspace"

        app = BrowserApp(syl, states, {"core": "core.02"}, ["core"], module="core.02")
        async with app.run_test(size=(150, 45)) as pilot:
            await pilot.pause()
            await pilot.press("g")
            await pilot.pause()
        assert app.return_value == ["goto", "core.02"], "g must make this the current module"

    asyncio.run(drive())


def test_home_animates_and_can_be_switched_off(home):
    from learn.home import HomeApp

    cli.main(["init"])
    data = cli._home_data()
    assert data["animations"] is True, "animations are on unless the learner turns them off"

    async def drive() -> None:
        app = HomeApp(data)
        async with app.run_test(size=(170, 50)) as pilot:
            await wait_until(pilot, lambda: app.poem.frame > 3, "the timer to step the scene")
            await wait_until(pilot, lambda: app.rain_left.drops and app.rain_right.drops, "rain in both empty areas")
            await wait_until(pilot, lambda: str(app.query_one("#rain-left").content).strip(), "the left rain to be drawn")
            await wait_until(pilot, lambda: ">>>" in str(app.query_one("#poem").content), "the poem to start with the prompt")
            assert app.query_one("#clockbox").region.x > app.query_one("#overview").region.x, \
                "the clock pane sits to the right of the plan"
            await pilot.press("q")

        narrow = HomeApp(data)
        async with narrow.run_test(size=(100, 40)) as pilot:
            await wait_until(pilot, lambda: narrow.query_one("#poem").display is False, "the poem to hide on a narrow terminal")
            assert narrow.query_one("#clock").display, "but the clock stays"
            await pilot.press("q")

        off = HomeApp({**data, "animations": False})
        async with off.run_test(size=(170, 50)) as pilot:
            await pilot.pause(0.5)
            assert off.poem.frame == 0, "with animations off nothing may move"
            assert off.query_one("#poem").display is False and off.query_one("#rain-left").display is False
            await pilot.press("q")

    asyncio.run(drive())

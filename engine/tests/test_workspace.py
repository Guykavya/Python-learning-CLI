"""The full-screen workspace (optional Textual extra) drives the same commands as the plain CLI."""

import asyncio
import shutil

import pytest

pytest.importorskip("textual", reason="optional extra: pip install -e '.[tui]'")

from learn import cli, content, db  # noqa: E402
from learn.workspace import WorkspaceApp  # noqa: E402

PID = "core.02.p001"


def _text(widget) -> str:
    """What a Static shows, as plain text."""
    import io

    from rich.console import Console

    console = Console(width=120, file=io.StringIO(), record=True)
    console.print(widget.content)
    return console.export_text()


def _state():
    conn = db.connect()
    try:
        return db.problem_state(conn, PID)
    finally:
        conn.close()


def test_workspace_hint_check_solution_flow(home):
    assert cli.main(["init"]) == 0
    assert cli.main(["start", PID]) == 0

    async def drive() -> None:
        app = WorkspaceApp(PID)
        async with app.run_test(size=(140, 45)) as pilot:
            await pilot.pause()
            assert "solution.py" in _text(app.query_one("#file")), "My file tab must show the learner's file"

            await pilot.press("s")  # no attempt yet: must ask, not show
            await pilot.pause()
            assert app.screen.__class__.__name__ == "ConfirmScreen", "solution before an attempt must ask first"
            await pilot.press("n")
            await pilot.pause()
            assert not _state()["solution_viewed"], "saying no must not mark the solution as viewed"

            await pilot.press("h")
            await pilot.pause()
            assert _state()["hints_used"] == 1, "h must use exactly one hint, like learn hint"
            assert "Hint 1" in app.query_one("#hints").source

            await pilot.press("c")  # the starter fails: a recorded failed check
            await app.workers.wait_for_complete()
            await pilot.pause()
            assert _state()["failed_checks"] == 1, "c must record a failed check, like learn check"
            assert "Not yet" in _text(app.query_one("#check"))
            assert "press h" in _text(app.query_one("#check")), "CLI words are translated to workspace keys"

            await pilot.press("s")  # after a failed check it still asks: one key is easy to hit by accident
            await pilot.pause()
            assert app.screen.__class__.__name__ == "ConfirmScreen", "an unsolved problem must confirm first"
            await pilot.press("y")
            await pilot.pause()
            assert _state()["solution_viewed"], "confirming must count as viewed, like learn solution"
            assert "Common mistakes" in app.query_one("#solution").source

            prob = content.get(PID)
            shutil.copy(prob.file("reference.py"), prob.work_path() / "solution.py")
            await pilot.press("c")
            await app.workers.wait_for_complete()
            await pilot.pause()
            assert _state()["status"] == "solved", "a passing check must solve the problem"

            await pilot.press("s")
            await pilot.pause()
            assert app.query_one("#side").active == "tab-solution", "after solving, s shows the walkthrough directly"
            await pilot.press("q")

    asyncio.run(drive())

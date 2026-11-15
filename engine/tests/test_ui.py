from learn import cli, completion, reader, ui


def test_sections_ignore_headings_inside_code():
    text = "# Title\nintro\n## One\n```python\n## not a heading\n```\n## Two\nend\n"
    sections = reader.split_sections(text)
    assert [s.title for s in sections] == ["Introduction", "One", "Two"]
    assert "## not a heading" in reader.render(sections[1].lines)


def test_completion_candidates(home):
    parser = cli.build_parser()
    assert "start" in completion.candidates(parser, ["st"])
    assert "core.02.p001" in completion.candidates(parser, ["start", "core.02"])
    assert "core.02" in completion.candidates(parser, ["read", ""])
    assert "--restart" in completion.candidates(parser, ["read", "--"])
    assert completion.candidates(parser, ["stats", ""]) == ["dsa", "topics"]
    assert completion.candidates(parser, ["start", "core.02.p001", ""]) == []


def test_menu_accepts_typed_commands():
    parser = cli.build_parser()
    assert cli._typed_command(parser, "check") == ["check"], "a bare command should run"
    assert cli._typed_command(parser, "./learn read core.03") == ["read", "core.03"], "drop the ./learn prefix"
    assert cli._typed_command(parser, ".\\learn.cmd start 1") == ["start", "1"], "drop the Windows launcher too"
    assert cli._typed_command(parser, "./learn start1") is None, "unknown words are not commands"
    assert cli._typed_command(parser, "./learn") is None, "the launcher alone is not a command"


def test_box_lines_have_equal_width(capsys):
    ui.box(ui.ok("✓ Solved") + " x", ["short", ui.dim("a longer line here")])
    widths = {ui.vis_len(line) for line in capsys.readouterr().out.splitlines()}
    assert len(widths) == 1


def test_answers_hidden_until_revealed():
    lines = ["Predict it.", "<details><summary>Answer</summary>", "", "secret 42", "", "</details>", "after"]
    assert "secret 42" not in reader.render(lines)
    assert "after" in reader.render(lines)
    assert "secret 42" in reader.render(lines, reveal=True)
    assert reader.has_answers(lines)


def test_markdown_reader_draws_tables_and_hides_answers():
    lines = [
        "## 1. Title",
        "| Name | Value |",
        "|---|---|",
        "| a | 1 |",
        "Prose with <class 'int'> and `code`.",
        "<details><summary>Answer</summary>",
        "",
        "secret 42",
        "",
        "</details>",
        "after",
    ]
    hidden = reader.render_markdown(lines)
    assert "secret 42" not in hidden, "answers must stay hidden until the learner presses a"
    assert "after" in hidden, "text after </details> must come back"
    assert "<class 'int'>" in hidden, "angle brackets in prose must not be swallowed as HTML"
    assert "|---|" not in hidden, "the table separator row should become a drawn rule, not raw text"
    assert "secret 42" in reader.render_markdown(lines, reveal=True)


def test_markdown_reader_keeps_code_fences_literal():
    lines = ["```python", "<details><summary>x</summary>", "a = [1, 2]", "```", "end"]
    out = reader.render_markdown(lines)
    assert "<details><summary>x</summary>" in out, "a <details> line inside a code fence is code, not a box"
    assert "end" in out


def test_tui_reader_navigates_and_hides_answers():
    import asyncio

    import pytest

    pytest.importorskip("textual", reason="optional extra: pip install -e '.[tui]'")
    from learn.tui import ReaderApp

    text = "Intro\n\n## 1. One\n\nPredict it.\n\n<details><summary>Answer</summary>\n\nsecret 42\n\n</details>\n\n## 2. Two\n\nlast"
    saved: list[int] = []

    async def drive() -> None:
        app = ReaderApp("t", text, 1, saved.append)
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            assert app.index == 1, "the reader must open where the learner stopped"
            assert "secret 42" not in app.section_source(), "answers stay hidden until a is pressed"
            await pilot.press("a")
            await pilot.pause()
            assert "secret 42" in app.section_source(), "a must reveal the answers"
            await pilot.press("n")
            await pilot.pause()
            assert app.index == 2 and not app.reveal, "next section starts with answers hidden again"
            await pilot.press("n")
            await pilot.pause()
            assert app.finished, "pressing next on the last section ends the chapter"
            await pilot.press("q")

    asyncio.run(drive())
    assert saved[0] == 1 and saved[-1] == 2, "every shown section must be saved as the reading position"

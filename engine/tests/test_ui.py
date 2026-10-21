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

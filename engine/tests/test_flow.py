import shutil

from learn import cli, content, db, progress, runner
from learn.syllabus import load


def run(*args):
    return cli.main(list(args))


def test_syllabus_prerequisites_exist(home):
    syl = load()
    ids = {m.id for m in syl.modules()}
    for m in syl.modules():
        for r in m.requires + m.requires_any:
            assert r in ids, f"{m.id} requires unknown {r}"


def test_validate_runs_on_a_problem(home):
    # Full content validation is `learn validate`; this only exercises the path quickly.
    assert run("validate", "dsa.00.p001") == 0


def test_solve_flow_records_progress(home, capsys):
    assert run("init") == 0
    assert run("start", "core.02.p001") == 0
    assert run("check") == 0          # starter fails, recorded as failed check
    prob = content.get("core.02.p001")
    shutil.copy(prob.file("reference.py"), prob.work_path() / "solution.py")
    assert run("check") == 0
    conn = db.connect()
    st = db.problem_state(conn, "core.02.p001")
    assert st["status"] == "solved"
    assert st["failed_checks"] == 1
    assert 0 < st["last_quality"] < 1
    assert st["review_due"] > db.today()
    assert db.day_count(conn) == 1


def test_trace_empty_answer_is_not_an_attempt(home):
    run("init")
    run("start", "core.02.p003")
    run("check")
    conn = db.connect()
    assert conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] == 0


def test_solution_requires_attempt(home):
    run("init")
    run("start", "core.02.p002")
    assert run("solution") == 1
    assert run("solution", "--force") == 0


def test_plan_skips_modules_without_content(home):
    shutil.rmtree(next((home / "content" / "core").glob("core.01-*")))
    content.reload()
    run("init")
    conn = db.connect()
    plan = progress.plan_today(conn, load(), {"plan": {"daily_minutes": 60, "focus": ["core", "dsa"]}})
    assert plan, "plan should not be empty when content exists"
    assert all(item.problem.module_id != "core.01" for item in plan if item.problem)
    assert any(item.track == "dsa" for item in plan)


def test_syllabus_is_honest_about_unwritten_modules(home, capsys):
    run("init")
    capsys.readouterr()
    run("syllabus", "swe")
    out = capsys.readouterr().out
    assert "not written yet" in out, "a module with no problems must say so, not show 0/N"
    assert "Written so far: 0 of" in out, "the summary line should count only modules that have problems"

    run("syllabus", "dsa")
    out = capsys.readouterr().out
    assert "Written so far: 2 of" in out, "dsa has two written modules"


def test_goto_warns_when_module_has_no_content(home, capsys):
    run("init")
    capsys.readouterr()
    run("goto", "swe.01")
    out = capsys.readouterr().out
    assert "no problems written yet" in out, "jumping to an unwritten module should warn that the plan will skip it"


def test_trace_normalise_ignores_comments_and_trailing_space():
    assert runner.normalise("# note\n1  \n2\n\n") == ["1", "2"]

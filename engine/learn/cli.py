"""The `learn` command. Run `learn --help` or `learn <command> --help`."""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from learn import completion, config, content, db, gitsnap, model, paths, progress, reader, runner, scan, sync, ui
from learn.syllabus import Syllabus
from learn.syllabus import load as load_syllabus

MAX_SESSION_SECONDS = 90 * 60
EXPLAIN_MIN_WORDS = 30
EXPLAIN_RATING_QUALITY = {1: 0.3, 2: 0.7, 3: 1.0}
STATUS_ICON = {"mastered": "★", "in-progress": "◐", "not-started": "○", "no-content": "·"}
KIND_FILE = {"code": "solution.py", "trace": "answer.txt", "explain": "answer.md"}


class UserError(Exception):
    """A problem the user can fix. Printed without a traceback."""


# ----------------------------------------------------------------- helpers

def ctx() -> tuple[sqlite3.Connection, Syllabus, dict]:
    if not paths.syllabus_path().exists():
        raise UserError(f"syllabus.yaml not found in {paths.root()}")
    return db.connect(), load_syllabus(), config.load()


def resolve_problem(conn: sqlite3.Connection, ref: str | None) -> content.Problem:
    if ref is None:
        ref = db.get_meta(conn, "last_problem")
        if not ref:
            raise UserError("Which problem? Example: learn check core.02.p001")
    if ref.isdigit():
        syl, cfg = load_syllabus(), config.load()
        plan = progress.plan_today(conn, syl, cfg)
        i = int(ref) - 1
        if not 0 <= i < len(plan):
            raise UserError(f"Today's plan has {len(plan)} item(s). Run: learn today")
        item = plan[i]
        if item.problem is None:
            raise UserError(f"Item {ref} is an external problem. Solve it on the site, then: "
                            f"learn log {_site_short(item.external['site'])} {item.external['key']}")
        return item.problem
    try:
        return content.get(ref)
    except KeyError as exc:
        raise UserError(str(exc.args[0])) from None


def _site_short(site: str) -> str:
    return {"leetcode": "lc", "codeforces": "cf", "cses": "cses"}.get(site, site)


def open_in_editor(*files: Path) -> None:
    exe = shutil.which("code")
    if exe:
        subprocess.Popen([exe, "-r", *map(str, files)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def want_editor(args: argparse.Namespace, cfg: dict) -> bool:
    return bool(getattr(args, "code", False) or cfg.get("editor", {}).get("open_in_vscode"))


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(paths.root()))
    except ValueError:
        return str(p)


def fmt_minutes(seconds: int) -> str:
    m = round(seconds / 60)
    return f"{m // 60}h {m % 60}m" if m >= 60 else f"{m}m"


def _touch_session(conn: sqlite3.Connection, st: sqlite3.Row) -> int:
    """Add time since the session timer was last touched (capped) and restart the timer."""
    seconds = 0
    if st["session_started"]:
        delta = datetime.now() - datetime.fromisoformat(st["session_started"])
        seconds = int(min(max(delta.total_seconds(), 0), MAX_SESSION_SECONDS))
    conn.execute(
        "UPDATE problem_state SET session_started = ?, seconds_spent = seconds_spent + ? WHERE problem_id = ?",
        (db.now(), seconds, st["problem_id"]),
    )
    db.mark_active(conn, seconds)
    return seconds


# ----------------------------------------------------------------- init

def cmd_init(args: argparse.Namespace) -> None:
    for d in (paths.content_dir(), paths.work_dir(), paths.playground_dir(), paths.library_dir(), paths.data_dir()):
        d.mkdir(parents=True, exist_ok=True)
    readmes = {
        paths.playground_dir() / "README.md": (
            "# Playground\n\nYour free zone. Create any files and folders here.\n"
            "Nothing is graded. `learn` only notices which Python features and libraries\n"
            "you use, and counts them as self-practice in `learn stats`.\n"
        ),
        paths.work_dir() / "README.md": (
            "# My work\n\nManaged by `learn`. Each problem you start gets its own folder here,\n"
            "organised as track/module/problem. Reviews go into a `reviews/<date>` subfolder,\n"
            "so your first solution is never overwritten.\n"
        ),
        paths.library_dir() / "README.md": (
            "# Library\n\nDrop books and notes (PDF) here. PDFs are kept out of Git on purpose,\n"
            "because they are large and usually copyrighted. Back them up separately.\n"
        ),
    }
    for path, text in readmes.items():
        if not path.exists():
            path.write_text(text)
    conn = db.connect()
    if not db.get_meta(conn, "created"):
        db.set_meta(conn, "created", db.today())
    conn.commit()
    print(ui.ok("Folders and tracker database are ready: ") + rel(paths.db_path()))
    print(gitsnap.init())
    print("\nNext:  " + ui.accent("learn today"))


# ----------------------------------------------------------------- today / next / resume

def cmd_today(args: argparse.Namespace) -> None:
    conn, syl, cfg = ctx()
    scan.scan(conn)
    conn.commit()
    plan = progress.plan_today(conn, syl, cfg)
    days = db.day_count(conn)
    focus = ", ".join(cfg["plan"].get("focus", []))
    print(ui.bold(f"Day {days + (0 if _active_today(conn) else 1)}") +
          ui.dim(f"  ·  {date.today():%a %d %b %Y}  ·  {cfg['plan']['daily_minutes']} min plan  ·  focus: {focus}"))
    if not content.all_problems():
        print("\n" + ui.warn("No problems in content/ yet.") +
              " The engine is ready; content gets added module by module.")
        print(ui.dim("Meanwhile: learn syllabus  ·  learn module core.01"))
        return
    if not plan:
        print("\nNothing planned. Every problem in your focus tracks is solved or none is due.")
        print(ui.dim("Change focus with: learn focus core dsa swe"))
        return
    print()
    total = 0
    tags = {"review": ui.warn("[Review]"), "new": ui.accent("[New]   "), "external": ui.style("[Site]  ", "magenta")}
    for i, item in enumerate(plan, 1):
        tag = tags[item.kind]
        if item.kind == "new" and item.track == "dsa":
            tag = ui.style("[DSA]   ", "magenta")
        tier = f"{item.problem.tier}/{item.problem.kind}" if item.problem else item.external.get("site", "")
        print(f"  {i}. {tag} {item.label}")
        print(ui.dim(f"       {tier} · ~{item.minutes} min · {item.reason}"))
        total += item.minutes
    print(ui.dim(f"\n  About {total} minutes.  Start with: learn next   (or learn start <number>)"))


def _active_today(conn: sqlite3.Connection) -> bool:
    return conn.execute("SELECT 1 FROM active_days WHERE day = ?", (db.today(),)).fetchone() is not None


def cmd_next(args: argparse.Namespace) -> None:
    conn, syl, cfg = ctx()
    for item in progress.plan_today(conn, syl, cfg):
        if item.problem is not None:
            args.problem = item.problem.id
            args.review = item.kind == "review"
            return cmd_start(args)
    print("Nothing left in today's plan. Run: learn today")


def cmd_resume(args: argparse.Namespace) -> None:
    conn, syl, cfg = ctx()
    last_day = conn.execute("SELECT MAX(day) FROM active_days").fetchone()[0]
    print(ui.bold(f"Welcome back. You have studied on {db.day_count(conn)} day(s)."))
    if last_day:
        gap = (date.today() - date.fromisoformat(last_day)).days
        print(f"Last study day: {last_day}" + (f"  ({gap} days ago)" if gap else "  (today)"))
    else:
        gap = 0
        print("No study days recorded yet.")
    open_rows = conn.execute(
        "SELECT problem_id, session_dir FROM problem_state WHERE status = 'started' ORDER BY session_started DESC LIMIT 3"
    ).fetchall()
    if open_rows:
        print("\nUnfinished problems:")
        for r in open_rows:
            print(f"  {r['problem_id']}   {ui.dim(rel(Path(r['session_dir'])))}")
    print("\nWhere you are:")
    for t in cfg["plan"].get("focus", []):
        if t in syl.track_ids():
            m = progress.current_module(conn, syl, t)
            print(f"  {t:7} {m.id} {m.title}")
    if gap >= 14:
        recent = conn.execute(
            "SELECT problem_id FROM problem_state WHERE status = 'solved' ORDER BY solved_at DESC LIMIT 3"
        ).fetchall()
        if recent:
            print("\n" + ui.warn("Long break.") + " Warm up by re-solving a few recent problems first:")
            for r in recent:
                print(f"  learn start {r[0]} --review")
    print()
    cmd_today(args)


# ----------------------------------------------------------------- start / check / hint / solution

def cmd_start(args: argparse.Namespace) -> None:
    conn, syl, cfg = ctx()
    prob = resolve_problem(conn, args.problem)
    st = db.problem_state(conn, prob.id)
    is_review = bool(getattr(args, "review", False)) or (
        st is not None and st["status"] == "solved"
        and st["review_due"] is not None and st["review_due"] <= db.today()
    )
    if st is not None and st["status"] == "solved" and not is_review:
        print(f"You already solved {prob.id}. Use --review to solve it again from scratch.")
        return

    base = prob.work_path()
    work = base / "reviews" / db.today() if is_review else base
    work.mkdir(parents=True, exist_ok=True)
    main_file = work / KIND_FILE.get(prob.kind, "solution.py")
    if not main_file.exists():
        if prob.kind == "code":
            starter = prob.file("starter.py")
            main_file.write_text(starter.read_text() if starter.exists() else "# Write your solution here\n")
        elif prob.kind == "trace":
            main_file.write_text("# Write the exact output you predict, line by line, below this comment.\n")
        else:
            main_file.write_text("<!-- Explain in your own words. At least a few sentences. -->\n\n")
    shutil.copy(prob.file("problem.md"), work / "problem.md")

    continuing = (
        st is not None and st["session_dir"] == str(work)
        and (st["status"] == "started" or bool(st["is_review"]))
    )
    if continuing:
        conn.execute("UPDATE problem_state SET session_started = ? WHERE problem_id = ?", (db.now(), prob.id))
    elif st is None:
        conn.execute(
            "INSERT INTO problem_state(problem_id, status, first_started, session_started, session_dir, "
            "is_review, difficulty) VALUES (?, 'started', ?, ?, ?, 0, ?)",
            (prob.id, db.now(), db.now(), str(work), prob.difficulty),
        )
    else:
        conn.execute(
            "UPDATE problem_state SET session_started = ?, session_dir = ?, is_review = ?, hints_used = 0, "
            "solution_viewed = 0, failed_checks = 0 WHERE problem_id = ?",
            (db.now(), str(work), int(is_review), prob.id),
        )
    db.set_meta(conn, "last_problem", prob.id)
    db.log_event(conn, "start", prob.id, "review" if is_review else None)
    db.mark_active(conn)
    conn.commit()

    label = "REVIEW  " if is_review else ""
    ui.heading(f"{label}{prob.id}  {prob.title}")
    print(ui.dim(f"{prob.tier} · {prob.kind} · ~{prob.minutes} min · topics: {', '.join(prob.topics)}"))
    print()
    print(prob.read("problem.md").strip())
    print()
    print(ui.bold("Your file: ") + rel(main_file))
    if is_review:
        print(ui.dim("Review = solve again from scratch without looking at your old solution."))
    print(ui.dim("When ready:  learn check   ·   stuck: learn hint   ·   chapter: learn read " + prob.module_id))
    if want_editor(args, cfg):
        open_in_editor(work / "problem.md", main_file)


def cmd_check(args: argparse.Namespace) -> None:
    conn, syl, cfg = ctx()
    prob = resolve_problem(conn, args.problem)
    st = db.problem_state(conn, prob.id)
    if st is None:
        raise UserError(f"Start it first: learn start {prob.id}")
    work = Path(st["session_dir"])
    practice_only = st["status"] == "solved" and not st["is_review"]
    scan.scan(conn)

    if prob.kind == "code":
        result = runner.run_code_tests(prob, work)
    elif prob.kind == "trace":
        result = runner.check_trace(prob, work / "answer.txt")
    else:
        result = _check_explain(prob, work, args)

    (work / ".last_check.txt").write_text(result.output)
    if result.not_ready and prob.kind != "code":
        print(ui.warn(result.output))
        return
    if practice_only:
        conn.commit()
        mark = ui.ok("✓ Passed") if result.passed else ui.err("✗ Not passing")
        if not result.passed:
            print(result.output.rstrip())
        print(f"{mark} {prob.id}. It was already solved, so progress is unchanged. "
              f"To practise it for credit: learn start {prob.id} --review")
        return
    seconds = _touch_session(conn, st)
    st = db.problem_state(conn, prob.id)
    q = None

    if result.passed:
        mastered_before = progress.module_progress(prob.module_id, db.states(conn)).mastered
        q = model.quality(st["hints_used"], st["failed_checks"], bool(st["solution_viewed"]))
        if prob.kind == "explain":
            q = min(q, EXPLAIN_RATING_QUALITY[result.self_rating or 2])
        user_before = progress.rating(conn, prob.track)
        user_after, prob_after = model.update_ratings(user_before, st["difficulty"] or prob.difficulty, q)
        conn.execute(
            "INSERT INTO ratings(track, rating) VALUES (?, ?) ON CONFLICT(track) DO UPDATE SET rating = excluded.rating",
            (prob.track, user_after),
        )
        interval = model.next_interval(st["review_interval"], q, bool(st["is_review"]))
        due = model.due_date(interval)
        conn.execute(
            "UPDATE problem_state SET status = 'solved', solved_at = COALESCE(solved_at, ?), "
            "best_quality = MAX(COALESCE(best_quality, 0), ?), last_quality = ?, review_due = ?, "
            "review_interval = ?, reviews_done = reviews_done + ?, difficulty = ?, is_review = 0 "
            "WHERE problem_id = ?",
            (db.now(), q, q, due, interval, int(bool(st["is_review"])), prob_after, prob.id),
        )
    else:
        conn.execute("UPDATE problem_state SET failed_checks = failed_checks + 1 WHERE problem_id = ?", (prob.id,))

    conn.execute(
        "INSERT INTO attempts(problem_id, at, passed, tests_passed, tests_total, seconds, hints_used, is_review, quality) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (prob.id, db.now(), int(result.passed), result.tests_passed, result.tests_total, seconds,
         st["hints_used"], st["is_review"], q),
    )
    conn.commit()

    if result.passed:
        mp = progress.module_progress(prob.module_id, db.states(conn))
        detail = (f"self-rating {result.self_rating}/3" if result.self_rating
                  else f"{result.tests_passed}/{result.tests_total} checks")
        _solve_screen(prob, st, q, detail, user_before, user_after, due, interval, mp)
        if mp.mastered and not mastered_before:
            print()
            ui.box(ui.style(f"★ Module {prob.module_id} mastered ★", "bold", "yellow"), [
                syl.module(prob.module_id).title,
                ui.dim("Its problems keep coming back as reviews so it stays fresh."),
            ], color="yellow")
        print(ui.dim("  Compare with the walkthrough: learn solution   ·   next: learn next"))
        gitsnap.snapshot(f"learn: solved {prob.id}" + (" (review)" if st["is_review"] else ""))
    else:
        print(result.output.rstrip())
        print()
        print(ui.err(f"✗ Not yet  {prob.id}") +
              ui.dim(f"  ({result.tests_passed}/{result.tests_total} checks passed)"))
        left = len(prob.hints()) - st["hints_used"]
        print(ui.dim(f"  Read the first failure carefully. Hints left: {left} (learn hint)."))


def _solve_screen(prob: content.Problem, st: sqlite3.Row, q: float, detail: str,
                  user_before: float, user_after: float, due: str, interval: float,
                  mp: model.ModuleProgress) -> None:
    dots = round(q * 5)
    slips = [f"{st['hints_used']} hint(s)" if st["hints_used"] else "",
             f"{st['failed_checks']} failed check(s)" if st["failed_checks"] else "",
             "solution viewed" if st["solution_viewed"] else ""]
    slips_text = " · ".join(s for s in slips if s) or "clean solve"
    delta = round(user_after) - round(user_before)
    arrow = ui.ok(f"▲ {delta}") if delta > 0 else ui.err(f"▼ {-delta}") if delta < 0 else ui.dim("=")
    days = round(interval)
    review = f"in {days} day{'s' if days != 1 else ''}  ·  {date.fromisoformat(due):%a %d %b}"
    title = (ui.ok("✓ Review passed" if st["is_review"] else "✓ Solved")
             + "  " + ui.bold(prob.id) + "  " + prob.title)
    def label(s: str) -> str:
        return ui.dim(f"{s:<9}")

    ui.box(title, [
        label("Quality") + ui.warn("●" * dots) + ui.dim("○" * (5 - dots)) + f"  {q:.2f}  " + ui.dim(slips_text),
        label("Checks") + detail,
        label("Time") + fmt_minutes(st["seconds_spent"]),
        label("Rating") + f"{prob.track} {user_before:.0f} → {user_after:.0f}  {arrow}",
        label("Review") + review,
        label("Module") + f"{prob.module_id}  {ui.bar(mp.score)}  {mp.solved}/{mp.total} solved",
    ])


def _check_explain(prob: content.Problem, work: Path, args: argparse.Namespace) -> runner.CheckResult:
    answer = work / "answer.md"
    words = runner.explain_word_count(answer)
    if words < EXPLAIN_MIN_WORDS:
        return runner.CheckResult(False, 0, 0,
                                  f"Your explanation has {words} words. Write at least {EXPLAIN_MIN_WORDS} in {answer}.")
    ui.heading("Model answer")
    print(prob.read("answer.md").strip())
    print()
    rating = getattr(args, "rate", None)
    while rating not in (1, 2, 3):
        raw = ui.ask("Compare honestly. 1 = missed key ideas, 2 = mostly right, 3 = fully covered")
        rating = int(raw) if raw.isdigit() else None
    if rating == 1:
        return runner.CheckResult(False, 0, 1, "Rewrite your explanation using what you just learned, then check again.",
                                  self_rating=1)
    return runner.CheckResult(True, 1, 1, "", self_rating=rating)


def cmd_hint(args: argparse.Namespace) -> None:
    conn, _, _ = ctx()
    prob = resolve_problem(conn, args.problem)
    st = db.problem_state(conn, prob.id)
    hints = prob.hints()
    if not hints:
        print("This problem has no hints. Try: learn read " + prob.module_id)
        return
    in_session = st is not None and (st["status"] == "started" or bool(st["is_review"]))
    used = st["hints_used"] if st is not None else 0
    if st is None or not in_session:
        for i, h in enumerate(hints, 1):
            print(ui.bold(f"Hint {i}") + f"\n{h}\n")
        return
    if used >= len(hints):
        print("No more hints. Next steps: learn stuck (ask a chatbot), or learn solution.")
        return
    conn.execute("UPDATE problem_state SET hints_used = hints_used + 1 WHERE problem_id = ?", (prob.id,))
    db.log_event(conn, "hint", prob.id, str(used + 1))
    conn.commit()
    print(ui.bold(f"Hint {used + 1} of {len(hints)}"))
    print(hints[used])
    if used + 1 < len(hints):
        print(ui.dim("\nTry again before asking for another hint."))


def cmd_solution(args: argparse.Namespace) -> None:
    conn, _, _ = ctx()
    prob = resolve_problem(conn, args.problem)
    st = db.problem_state(conn, prob.id)
    solved_now = st is not None and st["status"] == "solved"
    tried = st is not None and st["failed_checks"] > 0
    if not solved_now and not tried and not args.force:
        raise UserError("Make at least one real attempt first (learn check). "
                        "Use --force if you truly need it; the problem will come back for review sooner.")
    if st is not None and not solved_now:
        conn.execute("UPDATE problem_state SET solution_viewed = 1 WHERE problem_id = ?", (prob.id,))
        db.log_event(conn, "solution", prob.id)
        conn.commit()
    ui.heading(f"Walkthrough  {prob.id}  {prob.title}")
    print(prob.read("solution.md").strip() or "(no walkthrough written yet)")
    mistakes = prob.read("mistakes.md").strip()
    if mistakes:
        ui.heading("Common mistakes")
        print(mistakes)
    if not solved_now:
        print(ui.dim("\nNow close this, write it yourself from memory, and run learn check."))


def cmd_stuck(args: argparse.Namespace) -> None:
    conn, _, _ = ctx()
    prob = resolve_problem(conn, args.problem)
    st = db.problem_state(conn, prob.id)
    if st is None:
        raise UserError(f"Start it first: learn start {prob.id}")
    work = Path(st["session_dir"])
    main_file = work / KIND_FILE.get(prob.kind, "solution.py")
    last = (work / ".last_check.txt").read_text() if (work / ".last_check.txt").exists() else "(not checked yet)"
    seen = prob.hints()[: st["hints_used"]]
    lang = "python" if prob.kind == "code" else ""
    parts = [
        "I am learning Python and I am stuck on a practice problem.",
        "Please act as a tutor. Do NOT give me the full solution or full code.",
        "Ask me one guiding question or give one small hint about what I am missing, then stop.",
        "",
        "## Problem",
        prob.read("problem.md").strip(),
        "",
        "## My current attempt",
        f"```{lang}",
        main_file.read_text().strip() if main_file.exists() else "(empty)",
        "```",
        "",
        "## Result of my last check",
        "```",
        last.strip()[-3000:],
        "```",
    ]
    if seen:
        parts += ["", "## Hints I already used"] + [f"{i}. {h}" for i, h in enumerate(seen, 1)]
    text = "\n".join(parts) + "\n"
    out = work / "stuck_prompt.md"
    out.write_text(text)
    copied = _clipboard(text)
    print(ui.bold("Prompt ready: ") + rel(out))
    print("Paste it into any free chatbot." + (ui.ok(" (Copied to clipboard.)") if copied else ""))
    db.log_event(conn, "stuck", prob.id)
    conn.commit()


def _clipboard(text: str) -> bool:
    for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd, input=text, text=True, check=True, timeout=5)
                return True
            except Exception:
                continue
    return False


# ----------------------------------------------------------------- syllabus / module / read / goto / focus

def cmd_syllabus(args: argparse.Namespace) -> None:
    conn, syl, cfg = ctx()
    states = db.states(conn)
    tracks = [syl.track(args.track)] if args.track else syl.tracks
    for t in tracks:
        ui.heading(f"{t.id}  {t.title}")
        current = progress.current_module(conn, syl, t.id)
        for m in t.modules:
            mp = progress.module_progress(m.id, states)
            icon = STATUS_ICON[mp.status]
            pri = {"essential": "", "role-specific": ui.dim(" role"), "advanced-elective": ui.dim(" elective")}[m.priority]
            count = f"{mp.solved}/{mp.total}" if mp.total else ui.dim(f"0/{m.planned_problems} planned")
            here = ui.accent("  ← you are here") if m.id == current.id and t.id in cfg["plan"].get("focus", []) else ""
            print(f"  {icon} {m.id:9} {m.title}{pri}")
            print(ui.dim(f"      {count:>14}  ") + (ui.bar(mp.score) if mp.total else "") + here)
    print(ui.dim("\n  ★ mastered  ◐ in progress  ○ not started  · content not written yet"))


def cmd_module(args: argparse.Namespace) -> None:
    conn, syl, _ = ctx()
    try:
        m = syl.module(args.module)
    except KeyError as exc:
        raise UserError(str(exc.args[0])) from None
    states = db.states(conn)
    mp = progress.module_progress(m.id, states)
    ui.heading(f"{m.id}  {m.title}")
    print(ui.dim(f"{m.priority} · track {m.track} · status {mp.status}"))
    if m.requires or m.requires_any:
        req = ", ".join(m.requires) + (f" (any of {', '.join(m.requires_any)})" if m.requires_any else "")
        print(ui.dim(f"suggested first: {req}"))
    print("\n" + ui.bold("Topics"))
    for t in m.topics:
        print(f"  • {t}")
    print("\n" + ui.bold("You will be able to"))
    for o in m.learning_outcomes:
        print(f"  • {o}")
    if m.project:
        print("\n" + ui.bold("Project: ") + m.project)
    print("\n" + ui.bold("Chapter: ") + (rel(m.chapter_path) if m.chapter_path.exists() else ui.dim("not written yet")))
    probs = content.problems_for_module(m.id)
    print("\n" + ui.bold(f"Problems  {mp.solved}/{mp.total}") + ui.dim(f"  (planned {m.planned_problems})"))
    rows = []
    for p in probs:
        s = states.get(p.id)
        status = ui.dim("new")
        if s is not None:
            status = ui.ok(f"solved q={s['last_quality']:.2f}") if s["status"] == "solved" else ui.warn("started")
        due = s["review_due"] if s is not None and s["review_due"] else ""
        rows.append([p.short, p.title, f"{p.tier}/{p.kind}" + (f" [{p.assessment}]" if p.assessment else ""), status, due])
    if rows:
        ui.table(rows, header=["id", "title", "type", "status", "review"])
    if mp.assessments_available:
        missing = mp.assessments_available - mp.assessments_done
        print(ui.dim(f"\n  Assessments done: {', '.join(sorted(mp.assessments_done)) or 'none'}"
                     + (f"   still to do: {', '.join(sorted(missing))}" if missing else "")))


def cmd_read(args: argparse.Namespace) -> None:
    conn, syl, cfg = ctx()
    module_id = args.module
    if module_id is None:
        last = db.get_meta(conn, "last_problem")
        if not last:
            raise UserError("Which module? Example: learn read core.02")
        module_id = last.rsplit(".", 1)[0]
    try:
        m = syl.module(module_id)
    except KeyError as exc:
        raise UserError(str(exc.args[0])) from None
    if not m.chapter_path.exists():
        print(f"The chapter for {m.id} is not written yet. Topics it will cover:")
        for t in m.topics:
            print(f"  • {t}")
        return
    db.log_event(conn, "read", m.id)
    db.mark_active(conn)
    conn.commit()
    if args.code:
        print(ui.bold("Chapter: ") + rel(m.chapter_path))
        open_in_editor(m.chapter_path)
        print(ui.dim("Opened in VS Code. Press Ctrl+Shift+V there for the formatted preview."))
        return
    if args.print or not sys.stdin.isatty():
        print(m.chapter_path.read_text())
        return
    key = f"read_pos:{m.id}"

    def save(i: int) -> None:
        db.set_meta(conn, key, str(i))
        conn.commit()

    start = 0 if args.restart else int(db.get_meta(conn, key, "0"))
    reader.read_chapter(f"{m.id}  {m.title}", m.chapter_path.read_text(), start, save)


def cmd_goto(args: argparse.Namespace) -> None:
    conn, syl, _ = ctx()
    if args.auto:
        conn.execute("DELETE FROM track_cursor WHERE track = ?", (args.target,))
        conn.commit()
        print(f"{args.target}: back to automatic order (first module not yet mastered).")
        return
    try:
        m = syl.module(args.target)
    except KeyError as exc:
        raise UserError(str(exc.args[0])) from None
    conn.execute(
        "INSERT INTO track_cursor(track, module_id) VALUES (?, ?) "
        "ON CONFLICT(track) DO UPDATE SET module_id = excluded.module_id",
        (m.track, m.id),
    )
    db.log_event(conn, "goto", m.id)
    conn.commit()
    print(f"Track {m.track} now continues from {m.id} {m.title}.")
    print(ui.dim(f"Undo with: learn goto {m.track} --auto"))


def cmd_focus(args: argparse.Namespace) -> None:
    _, syl, _ = ctx()
    bad = [t for t in args.tracks if t not in syl.track_ids()]
    if bad:
        raise UserError(f"Unknown track(s): {', '.join(bad)}. Tracks: {', '.join(syl.track_ids())}")
    config.set_value("plan.focus", list(args.tracks))
    print("Daily plan now draws from: " + ", ".join(args.tracks))


# ----------------------------------------------------------------- review / stats

def cmd_review(args: argparse.Namespace) -> None:
    conn, _, _ = ctx()
    due = progress.due_reviews(conn)
    soon = (date.today() + timedelta(days=7)).isoformat()
    upcoming = conn.execute(
        "SELECT problem_id, review_due FROM problem_state WHERE status = 'solved' AND review_due > ? "
        "AND review_due <= ? ORDER BY review_due", (db.today(), soon)).fetchall()
    ui.heading(f"Reviews due now: {len(due)}")
    for p, row in due:
        print(f"  {p.id:16} {p.title:40} {ui.dim('due ' + row['review_due'])}")
    if upcoming:
        ui.heading("Coming up this week")
        for r in upcoming:
            print(f"  {r['problem_id']:16} {ui.dim(r['review_due'])}")
    if due:
        print(ui.dim("\nStart one with: learn start <id>   (reviews start from a blank file)"))


def cmd_stats(args: argparse.Namespace) -> None:
    conn, syl, cfg = ctx()
    scan.scan(conn)
    conn.commit()
    if args.view == "dsa":
        return _stats_dsa(conn, syl)
    if args.view == "topics":
        return _stats_topics(conn)
    states = db.states(conn)
    days = db.day_count(conn)
    secs = conn.execute("SELECT COALESCE(SUM(seconds), 0) FROM active_days").fetchone()[0]
    solved = [s for s in states.values() if s["status"] == "solved"]
    attempts = conn.execute("SELECT COUNT(*), COALESCE(SUM(passed), 0) FROM attempts").fetchone()
    reviews = conn.execute("SELECT COUNT(*) FROM attempts WHERE is_review = 1 AND passed = 1").fetchone()[0]
    hints = conn.execute("SELECT COUNT(*) FROM events WHERE kind = 'hint'").fetchone()[0]
    ext = conn.execute("SELECT site, COUNT(*) FROM external_solves GROUP BY site").fetchall()

    ui.heading("Overall")
    ui.table([
        ["Study days", str(days)],
        ["Time studied", fmt_minutes(secs)],
        ["Problems solved", str(len(solved))],
        ["Checks run / passed", f"{attempts[0]} / {attempts[1]}"],
        ["Reviews passed", str(reviews)],
        ["Hints used", str(hints)],
        ["External solves", ", ".join(f"{s} {n}" for s, n in ext) or "none yet"],
    ])
    ui.heading("Tracks")
    rows = []
    for t in syl.tracks:
        total = solved_n = 0
        mastered = 0
        for m in t.modules:
            mp = progress.module_progress(m.id, states)
            total += mp.total
            solved_n += mp.solved
            mastered += mp.mastered
        if total == 0 and t.id not in cfg["plan"].get("focus", []):
            continue
        rows.append([t.id, f"{solved_n}/{total}", f"{mastered}/{len(t.modules)} mastered",
                     f"{progress.rating(conn, t.id):.0f}"])
    ui.table(rows, header=["track", "solved", "modules", "rating"])

    weak = []
    for m in syl.modules():
        mp = progress.module_progress(m.id, states)
        if mp.solved and mp.avg_quality < model.MASTERY_QUALITY:
            weak.append((mp.avg_quality, m))
    if weak:
        ui.heading("Weakest modules (low average quality)")
        for q, m in sorted(weak, key=lambda x: x[0])[:5]:
            print(f"  {m.id:9} {m.title:42} quality {q:.2f}")
    practice = scan.self_practice(conn)
    if practice:
        ui.heading("Self-practice in playground (files per module)")
        top = sorted(practice.items(), key=lambda kv: -kv[1])[:8]
        print("  " + "   ".join(f"{m} {n}" for m, n in top))
    print(ui.dim("\n  More: learn stats dsa  ·  learn stats topics"))


def _stats_topics(conn: sqlite3.Connection) -> None:
    states = db.states(conn)
    per_topic: dict[str, list[float]] = {}
    for pid, s in states.items():
        if s["status"] != "solved" or pid not in content.all_problems():
            continue
        for t in content.all_problems()[pid].topics:
            per_topic.setdefault(t, []).append(s["last_quality"] or 0)
    if not per_topic:
        print("No solved problems yet.")
        return
    ui.heading("Topics, weakest first")
    rows = [[t, str(len(qs)), f"{sum(qs) / len(qs):.2f}", ui.bar(sum(qs) / len(qs))]
            for t, qs in sorted(per_topic.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))]
    ui.table(rows, header=["topic", "solved", "quality", ""])


def _stats_dsa(conn: sqlite3.Connection, syl: Syllabus) -> None:
    states = db.states(conn)
    ext: dict[str, dict[str, int]] = {}
    for r in conn.execute("SELECT site, modules FROM external_solves"):
        for m in filter(None, (r["modules"] or "").split(",")):
            ext.setdefault(m, {}).setdefault(r["site"], 0)
            ext[m][r["site"]] += 1
    unmapped = conn.execute(
        "SELECT COUNT(*) FROM external_solves WHERE modules IS NULL OR modules = ''").fetchone()[0]
    rows, gaps = [], []
    for m in syl.track("dsa").modules:
        mp = progress.module_progress(m.id, states)
        e = ext.get(m.id, {})
        lc, cf, cs = e.get("leetcode", 0), e.get("codeforces", 0), e.get("cses", 0)
        total = mp.solved + lc + cf + cs
        if total == 0:
            gaps.append(m)
        rows.append([m.id, m.title[:34], str(mp.solved), str(lc), str(cf), str(cs),
                     ui.bar(min(1.0, total / max(m.planned_problems * 0.5, 1)))])
    ui.heading("DSA by pattern")
    ui.table(rows, header=["module", "pattern", "local", "LC", "CF", "CSES", "practice"])
    for site in ("codeforces", "leetcode"):
        r = conn.execute("SELECT fetched_at, summary FROM external_stats WHERE site = ?", (site,)).fetchone()
        if r:
            print(ui.dim(f"  {site}: {r['summary']}  (synced {r['fetched_at']})"))
    if unmapped:
        print(ui.dim(f"  {unmapped} external solve(s) have no pattern yet. Set one with learn log <site> <key> --module dsa.XX"))
    if gaps:
        print("\n" + ui.warn("Never practised: ") + ", ".join(m.id for m in gaps))


# ----------------------------------------------------------------- external: log / sync

SITE_ALIASES = {"lc": "leetcode", "leetcode": "leetcode", "cf": "codeforces", "codeforces": "codeforces", "cses": "cses"}


def cmd_log(args: argparse.Namespace) -> None:
    conn, syl, cfg = ctx()
    site = SITE_ALIASES[args.site]
    key = args.key.strip().strip("/").split("/")[-1] if site == "leetcode" else args.key.strip()
    existing = conn.execute(
        "SELECT * FROM external_solves WHERE site = ? AND problem_key = ?", (site, key)).fetchone()

    title = existing["title"] if existing else None
    url = existing["url"] if existing else None
    tags = existing["tags"] if existing else ""
    difficulty = existing["difficulty"] if existing else None
    suggested = existing["modules"] if existing and existing["modules"] else ""
    if site == "leetcode" and not existing:
        info = sync.leetcode_question(key)
        if info:
            title, difficulty = info["title"], info["difficulty"]
            tag_list = [t["slug"] for t in info.get("topicTags", [])]
            tags = ",".join(tag_list)
            suggested = ",".join(sync.modules_for_tags(tag_list, sync.LC_TAG_MODULES))
        url = f"https://leetcode.com/problems/{key}/"
    elif site == "codeforces" and not url:
        import re
        m = re.fullmatch(r"(\d+)([A-Za-z]\d?)", key)
        if m:
            url = f"https://codeforces.com/problemset/problem/{m.group(1)}/{m.group(2).upper()}"
    elif site == "cses" and not url:
        url = f"https://cses.fi/problemset/task/{key}"

    interactive = sys.stdin.isatty() and not args.yes
    if title:
        print(ui.bold(f"{site}: {title}") + (ui.dim(f"  [{difficulty}]") if difficulty else ""))
    if tags:
        print(ui.dim(f"tags: {tags}"))
    modules = args.module or suggested
    if interactive:
        title = title or ui.ask("Problem title", key)
        modules = ui.ask("DSA module(s), e.g. dsa.03 (see learn syllabus dsa)", modules)
    minutes = args.minutes if args.minutes is not None else (int(ui.ask("Minutes taken", "30")) if interactive else None)
    hints = args.hints if args.hints is not None else (int(ui.ask("Hints or help used (0 if none)", "0")) if interactive else None)
    insight = args.insight or (ui.ask("Key insight in one or two lines") if interactive else None)

    for m in filter(None, (modules or "").split(",")):
        try:
            syl.module(m.strip())
        except KeyError:
            raise UserError(f"Unknown module '{m}'. DSA modules: dsa.00 to dsa.17") from None

    code_dir = paths.work_dir() / "dsa" / site
    code_dir.mkdir(parents=True, exist_ok=True)
    code_file = code_dir / f"{paths.slugify(key) or key}.py"
    if not code_file.exists():
        code_file.write_text(
            f'"""{site}: {title or key}\n{url or ""}\nPattern: {modules or "?"}\n'
            f'Insight: {insight or ""}\n"""\n\n# Paste your final accepted code below.\n'
        )
    conn.execute(
        "INSERT INTO external_solves(site, problem_key, title, url, tags, difficulty, modules, solved_at, minutes, "
        "hints, insight, code_path, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'log') "
        "ON CONFLICT(site, problem_key) DO UPDATE SET title = COALESCE(excluded.title, title), "
        "url = COALESCE(excluded.url, url), modules = COALESCE(NULLIF(excluded.modules, ''), modules), "
        "minutes = COALESCE(excluded.minutes, minutes), hints = COALESCE(excluded.hints, hints), "
        "insight = COALESCE(excluded.insight, insight), code_path = excluded.code_path",
        (site, key, title, url, tags, difficulty, modules, db.now(), minutes, hints, insight, str(code_file)),
    )
    db.mark_active(conn, (minutes or 0) * 60)
    db.log_event(conn, "log", f"{site}:{key}")
    conn.commit()
    print(ui.ok(f"Logged {site}:{key}") + (f"  → {modules}" if modules else ""))
    print(ui.bold("Save your code in: ") + rel(code_file))
    gitsnap.snapshot(f"learn: logged {site}:{key}")


def cmd_sync(args: argparse.Namespace) -> None:
    conn, _, cfg = ctx()
    targets = ["codeforces", "leetcode"] if args.site == "all" else [SITE_ALIASES[args.site]]
    for site in targets:
        try:
            if site == "codeforces":
                total, new, summary = sync.sync_codeforces(conn, cfg["accounts"].get("codeforces_handle", ""))
            else:
                total, new, summary = sync.sync_leetcode(conn, cfg["accounts"].get("leetcode_username", ""))
        except sync.SyncError as exc:
            print(ui.err(f"{site}: {exc}"))
            continue
        conn.commit()
        print(ui.ok(f"{site}: ") + f"{total} accepted found, {new} new.  {summary}")
    gitsnap.snapshot("learn: sync external solves")


# ----------------------------------------------------------------- config / scan

def cmd_config(args: argparse.Namespace) -> None:
    if args.action == "show":
        print(paths.config_path().read_text() if paths.config_path().exists() else "(no config.toml yet)")
    elif args.action == "get":
        print(config.get(args.key))
    else:
        if args.value is None:
            raise UserError("Usage: learn config set section.name value")
        config.set_value(args.key, config.parse_cli_value(args.value))
        print(f"{args.key} = {config.get(args.key)}")


def cmd_scan(args: argparse.Namespace) -> None:
    conn, _, _ = ctx()
    n = scan.scan(conn)
    conn.commit()
    print(f"Scanned playground: {n} new or changed file(s).")
    for r in conn.execute("SELECT path, features, modules FROM playground_files ORDER BY scanned_at DESC LIMIT 10"):
        feats = [f for f in r["features"].split(",") if f]
        print(f"  {r['path']}")
        print(ui.dim(f"     {', '.join(feats[:12])}{' …' if len(feats) > 12 else ''}"))


# ----------------------------------------------------------------- authoring: new / validate

def cmd_new(args: argparse.Namespace) -> None:
    _, syl, _ = ctx()
    try:
        m = syl.module(args.module)
    except KeyError as exc:
        raise UserError(str(exc.args[0])) from None
    probs_dir = m.content_path / "problems"
    probs_dir.mkdir(parents=True, exist_ok=True)
    numbers = [int(p.name[1:4]) for p in probs_dir.iterdir() if p.is_dir() and p.name[1:4].isdigit()]
    n = max(numbers, default=0) + 1
    slug = paths.slugify(args.title)
    folder = probs_dir / f"p{n:03d}-{slug}"
    folder.mkdir()
    pid = f"{m.id}.p{n:03d}"
    from learn import templates
    for name, text in templates.problem_files(pid, args.title, args.tier, args.kind).items():
        (folder / name).write_text(text)
    content.reload()
    print(ui.ok("Created ") + rel(folder))
    print(ui.dim("Fill in the files, then run: learn validate " + m.id))


def cmd_validate(args: argparse.Namespace) -> None:
    content.reload()
    probs = list(content.all_problems().values())
    if args.target:
        probs = [p for p in probs if p.id == args.target or p.module_id == args.target or p.track == args.target]
    if not probs:
        print("No problems found to validate.")
        return
    bad = 0
    for p in probs:
        issues = []
        required = ["problem.md", "hints.md", "solution.md", "mistakes.md"]
        required += {"code": ["starter.py", "test_solution.py", "reference.py"],
                     "trace": ["expected.txt"], "explain": ["answer.md"]}.get(p.kind, [])
        issues += [f"missing {f}" for f in required if not p.file(f).exists()]
        if p.kind not in content.KINDS:
            issues.append(f"unknown kind '{p.kind}'")
        if p.tier not in content.TIERS:
            issues.append(f"unknown tier '{p.tier}'")
        if p.file("hints.md").exists() and len(p.hints()) < 2:
            issues.append("fewer than 2 hints")
        if p.kind == "code" and p.file("reference.py").exists() and p.file("test_solution.py").exists():
            r = runner.run_code_tests(p, p.path, solution_file=p.file("reference.py"))
            if not r.passed:
                issues.append(f"reference.py fails its own tests ({r.tests_passed}/{r.tests_total})")
            if p.file("starter.py").exists():
                s = runner.run_code_tests(p, p.path, solution_file=p.file("starter.py"))
                if s.passed:
                    issues.append("starter.py already passes the tests")
        if issues:
            bad += 1
            print(ui.err("✗ ") + p.id + ui.dim("  " + "; ".join(issues)))
        elif args.verbose:
            print(ui.ok("✓ ") + p.id)
    print(f"\n{len(probs) - bad}/{len(probs)} problems valid.")
    if bad:
        raise SystemExit(1)


# ----------------------------------------------------------------- parser

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="learn", description="Your offline Python learning module.")
    sub = p.add_subparsers(dest="command")

    def add(name: str, func, help_text: str, aliases: list[str] | None = None) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=help_text, description=help_text, aliases=aliases or [])
        sp.set_defaults(func=func)
        return sp

    add("init", cmd_init, "Create folders, the tracker database and the Git repository")
    add("today", cmd_today, "Show today's plan (the default command)")
    sp = add("next", cmd_next, "Start the next item in today's plan")
    sp.add_argument("--code", action="store_true", help="open files in VS Code")
    add("resume", cmd_resume, "Pick up where you left off, even after a long break")

    sp = add("start", cmd_start, "Start a problem (id, or its number in today's plan)", aliases=["open"])
    sp.add_argument("problem")
    sp.add_argument("--review", action="store_true", help="solve a solved problem again from scratch")
    sp.add_argument("--code", action="store_true", help="open files in VS Code")
    sp = add("check", cmd_check, "Check your current problem")
    sp.add_argument("problem", nargs="?")
    sp.add_argument("--rate", type=int, choices=[1, 2, 3], help="self-rating for explain problems")
    sp = add("hint", cmd_hint, "Reveal the next hint")
    sp.add_argument("problem", nargs="?")
    sp = add("solution", cmd_solution, "Show the walkthrough and common mistakes")
    sp.add_argument("problem", nargs="?")
    sp.add_argument("--force", action="store_true")
    sp = add("stuck", cmd_stuck, "Build a paste-ready prompt for any free chatbot")
    sp.add_argument("problem", nargs="?")

    sp = add("syllabus", cmd_syllabus, "Show all tracks and modules with progress")
    sp.add_argument("track", nargs="?")
    sp = add("module", cmd_module, "Show one module: topics, outcomes, problems")
    sp.add_argument("module")
    sp = add("read", cmd_read, "Read a module's chapter here, section by section")
    sp.add_argument("module", nargs="?")
    sp.add_argument("--restart", action="store_true", help="start from the first section")
    sp.add_argument("--print", action="store_true", help="print the raw chapter in one go")
    sp.add_argument("--code", action="store_true", help="open it in VS Code instead")
    sp = add("goto", cmd_goto, "Jump a track to any module (nothing is locked)")
    sp.add_argument("target", help="module id, or a track id with --auto")
    sp.add_argument("--auto", action="store_true", help="return the track to automatic order")
    sp = add("focus", cmd_focus, "Choose which tracks feed the daily plan")
    sp.add_argument("tracks", nargs="+")

    add("review", cmd_review, "List reviews due now and this week")
    sp = add("stats", cmd_stats, "Progress statistics")
    sp.add_argument("view", nargs="?", choices=["dsa", "topics"])

    sp = add("log", cmd_log, "Log a LeetCode, Codeforces or CSES solve")
    sp.add_argument("site", choices=sorted(SITE_ALIASES))
    sp.add_argument("key", help="LeetCode slug or URL, Codeforces id like 1520A, CSES task id")
    sp.add_argument("--module", help="DSA module id(s), comma separated")
    sp.add_argument("--minutes", type=int)
    sp.add_argument("--hints", type=int)
    sp.add_argument("--insight")
    sp.add_argument("--yes", "-y", action="store_true", help="do not ask questions")
    sp = add("sync", cmd_sync, "Sync solves from Codeforces and LeetCode")
    sp.add_argument("site", nargs="?", default="all", choices=["all", "cf", "lc", "codeforces", "leetcode"])

    sp = add("config", cmd_config, "Show or change settings in config.toml")
    sp.add_argument("action", choices=["show", "get", "set"], nargs="?", default="show")
    sp.add_argument("key", nargs="?")
    sp.add_argument("value", nargs="?")
    add("scan", cmd_scan, "Scan the playground for self-practice")
    add("completion", cmd_completion, "Show how to turn on Tab completion in bash")

    sp = add("new", cmd_new, "Create a new problem from the template (authoring)")
    sp.add_argument("module")
    sp.add_argument("title")
    sp.add_argument("--tier", default="drill", choices=content.TIERS)
    sp.add_argument("--kind", default="code", choices=content.KINDS)
    sp = add("validate", cmd_validate, "Check problems are complete and their tests work (authoring)")
    sp.add_argument("target", nargs="?", help="problem, module or track id")
    sp.add_argument("-v", "--verbose", action="store_true")
    return p


# ----------------------------------------------------------------- menu / completion

MENU = [
    ("1", "Start next problem", ["next"]),
    ("2", "Check my answer", ["check"]),
    ("3", "Get a hint", ["hint"]),
    ("4", "Show the solution", ["solution"]),
    ("5", "Stuck: chatbot prompt", ["stuck"]),
    ("6", "Read the chapter", ["read"]),
    ("7", "Today's plan", ["today"]),
    ("8", "Syllabus", ["syllabus"]),
    ("9", "Stats", ["stats"]),
    ("10", "Start a problem by id", None),
]


def _print_menu(conn: sqlite3.Connection) -> None:
    print()
    last = db.get_meta(conn, "last_problem")
    st = db.problem_state(conn, last) if last else None
    if st is not None and (st["status"] == "started" or st["is_review"]):
        print(ui.dim("  Working on: ") + ui.bold(last) + "  " + content.get(last).title)
    half = (len(MENU) + 1) // 2
    for left, right in zip(MENU[:half], MENU[half:] + [None]):
        cell = f"  {ui.accent(f'{left[0]:>2}')}  {left[1]:<24}"
        print(cell + (f"{ui.accent(f'{right[0]:>2}')}  {right[1]}" if right else ""))
    print(f"  {ui.accent(' q')}  Quit")


def _ask_problem_id() -> str:
    """input() with Tab completion over problem ids."""
    try:
        import readline

        ids = sorted(content.all_problems())
        readline.set_completer(lambda text, i: ([p for p in ids if p.startswith(text)] + [None])[i])
        readline.set_completer_delims(" ")
        readline.parse_and_bind("tab: complete")
    except ImportError:
        pass
    return ui.ask("  Problem id (Tab completes)")


def cmd_menu(parser: argparse.ArgumentParser) -> None:
    """Plain `learn` in a terminal: today's plan, then a numbered menu until q."""
    cmd_today(argparse.Namespace())
    conn = db.connect()
    while True:
        _print_menu(conn)
        try:
            choice = input(ui.bold("\n  Choose: ")).strip().lower()
        except EOFError:
            choice = "q"
        if choice in ("q", "quit", "exit"):
            return
        entry = next((m for m in MENU if m[0] == choice), None)
        if entry is None:
            print(ui.warn("  Type a number from the menu, or q to quit."))
            continue
        argv = entry[2]
        if argv is None:
            pid = _ask_problem_id()
            if not pid:
                continue
            argv = ["start", pid]
        print()
        try:
            args = parser.parse_args(argv)
            args.func(args)
        except UserError as exc:
            print(ui.err(str(exc)))
        except KeyboardInterrupt:
            print()
        except SystemExit:
            pass


def cmd_completion(args: argparse.Namespace) -> None:
    script = paths.root() / "engine" / "completion.bash"
    print("Add this line to ~/.bashrc, then open a new terminal:\n")
    print(f'  [ -f "{script}" ] && . "{script}"')


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["_complete"]:
        completion.complete(parser, argv[1:])
        return 0
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func in (None, cmd_today, cmd_resume):
        ui.banner()
    try:
        if func is not None:
            func(args)
        elif sys.stdin.isatty() and sys.stdout.isatty():
            cmd_menu(parser)
        else:
            cmd_today(args)
    except UserError as exc:
        print(ui.err(str(exc)), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print()
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

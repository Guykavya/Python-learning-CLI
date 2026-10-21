"""Turn raw tracker data into progress, current position and today's plan."""

from __future__ import annotations

import sqlite3
import tomllib
from dataclasses import dataclass
from datetime import date

from learn import content, db, model
from learn.content import Problem
from learn.syllabus import Module, Syllabus

TIER_ORDER = {t: i for i, t in enumerate(content.TIERS)}


def module_progress(module_id: str, states: dict[str, sqlite3.Row]) -> model.ModuleProgress:
    probs = content.problems_for_module(module_id)
    solved = [p for p in probs if states.get(p.id) is not None and states[p.id]["status"] == "solved"]
    qualities = [states[p.id]["last_quality"] or 0.0 for p in solved]
    avg = sum(qualities) / len(qualities) if qualities else 0.0
    available = {p.assessment for p in probs if p.assessment}
    done = {
        p.assessment for p in solved
        if p.assessment and (states[p.id]["last_quality"] or 0) >= 0.6
    }
    return model.ModuleProgress(len(probs), len(solved), avg, done, available)


def rating(conn: sqlite3.Connection, track: str) -> float:
    row = conn.execute("SELECT rating FROM ratings WHERE track = ?", (track,)).fetchone()
    return row[0] if row else model.START_RATING


def current_module(conn: sqlite3.Connection, syl: Syllabus, track: str) -> Module:
    row = conn.execute("SELECT module_id FROM track_cursor WHERE track = ?", (track,)).fetchone()
    if row:
        try:
            return syl.module(row[0])
        except KeyError:
            pass
    states = db.states(conn)
    modules = syl.track(track).modules
    for m in modules:
        prog = module_progress(m.id, states)
        if prog.has_content and not prog.mastered:
            return m
    for m in modules:
        if not module_progress(m.id, states).mastered:
            return m
    return modules[-1]


def unsolved(module_id: str, states: dict[str, sqlite3.Row], user_rating: float) -> list[Problem]:
    probs = [
        p for p in content.problems_for_module(module_id)
        if states.get(p.id) is None or states[p.id]["status"] != "solved"
    ]

    def key(p: Problem) -> tuple:
        started = 0 if states.get(p.id) is not None else 1
        return (started, TIER_ORDER.get(p.tier, 9), abs(p.difficulty - user_rating), p.id)

    return sorted(probs, key=key)


def due_reviews(conn: sqlite3.Connection, on: str | None = None) -> list[tuple[Problem, sqlite3.Row]]:
    on = on or db.today()
    rows = conn.execute(
        "SELECT * FROM problem_state WHERE status = 'solved' AND review_due IS NOT NULL "
        "AND review_due <= ? ORDER BY review_due",
        (on,),
    ).fetchall()
    problems = content.all_problems()
    return [(problems[r["problem_id"]], r) for r in rows if r["problem_id"] in problems]


def external_list(module: Module) -> list[dict]:
    f = module.content_path / "external.toml"
    if not f.exists():
        return []
    with f.open("rb") as fh:
        return list(tomllib.load(fh).get("problem", []))


def external_done(conn: sqlite3.Connection) -> set[tuple[str, str]]:
    return {(r[0], r[1]) for r in conn.execute("SELECT site, problem_key FROM external_solves")}


@dataclass
class PlanItem:
    kind: str            # review | new | external
    track: str
    minutes: int
    reason: str
    problem: Problem | None = None
    external: dict | None = None

    @property
    def label(self) -> str:
        if self.problem:
            return f"{self.problem.id}  {self.problem.title}"
        e = self.external or {}
        return f"{e.get('site', '?')}:{e.get('key', '?')}  {e.get('title', '')}"


def plan_today(conn: sqlite3.Connection, syl: Syllabus, cfg: dict) -> list[PlanItem]:
    budget = int(cfg["plan"].get("daily_minutes", 60))
    focus = [t for t in cfg["plan"].get("focus", ["core", "dsa"]) if t in syl.track_ids()]
    states = db.states(conn)
    items: list[PlanItem] = []

    # 1. reviews, up to 40% of the day (at least one if any are due)
    review_budget = budget * 0.4
    used = 0
    for prob, row in due_reviews(conn):
        if items and used + prob.minutes > review_budget:
            break
        overdue = (date.today() - date.fromisoformat(row["review_due"])).days
        reason = "review due today" if overdue <= 0 else f"review overdue by {overdue} day(s)"
        items.append(PlanItem("review", prob.track, prob.minutes, reason, problem=prob))
        used += prob.minutes

    # 2. new work split across focus tracks; DSA gets a third when sharing
    remaining = max(0, budget - used)
    shares: dict[str, float] = {}
    if focus:
        if "dsa" in focus and len(focus) > 1:
            shares["dsa"] = remaining * 0.35
            others = [t for t in focus if t != "dsa"]
            for t in others:
                shares[t] = remaining * 0.65 / len(others)
        else:
            for t in focus:
                shares[t] = remaining / len(focus)

    done_ext = external_done(conn)
    for track in focus:
        share = shares.get(track, 0)
        spent = 0
        user_rating = rating(conn, track)
        modules = syl.track(track).modules
        start = current_module(conn, syl, track)
        idx = modules.index(start)
        added = 0
        for m in modules[idx:]:
            leftover = False
            for prob in unsolved(m.id, states, user_rating):
                if added and spent + prob.minutes > share:
                    leftover = True
                    break
                reason = f"{m.id} {m.title}" + (" (continue)" if prob.id in states else "")
                items.append(PlanItem("new", track, prob.minutes, reason, problem=prob))
                spent += prob.minutes
                added += 1
            if track == "dsa" and not leftover:
                for ext in external_list(m):
                    if (ext.get("site"), str(ext.get("key"))) in done_ext:
                        continue
                    mins = int(ext.get("minutes", 30))
                    if added and spent + mins > share:
                        leftover = True
                        break
                    items.append(PlanItem("external", track, mins, f"{m.id} {m.title}", external=ext))
                    spent += mins
                    added += 1
            if leftover or spent >= share:
                break
    return items

"""The learner model: quality of a solve, spaced repetition, ratings, mastery.

Everything here is plain arithmetic so it runs forever with no AI.

quality      0.1 to 1.0. 1.0 = solved first try with no hints.
review gaps  grow when you solve cleanly, shrink when you struggle.
ratings      Elo-style. Your rating per track rises when you beat harder problems.
mastery      per module: coverage of its problems times average quality,
             plus a check that all four assessment types are done.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

HINT_PENALTY = 0.15
FAIL_PENALTY = 0.05
SOLUTION_CAP = 0.2
MIN_QUALITY = 0.1

START_RATING = 1000.0
K_USER = 32.0
K_PROBLEM = 8.0

MASTERY_COVERAGE = 0.7
MASTERY_QUALITY = 0.7
ASSESSMENT_KINDS = ("explain", "trace", "fix", "build")


def quality(hints_used: int, failed_checks: int, solution_viewed: bool) -> float:
    q = 1.0 - HINT_PENALTY * hints_used - FAIL_PENALTY * failed_checks
    if solution_viewed:
        q = min(q, SOLUTION_CAP)
    return round(max(MIN_QUALITY, min(1.0, q)), 3)


def next_interval(previous: float | None, q: float, is_review: bool) -> float:
    """Days until the next review."""
    if q <= SOLUTION_CAP:
        return 1.0
    if not is_review or previous is None:
        if q >= 0.85:
            return 7.0
        if q >= 0.6:
            return 4.0
        return 2.0
    if q < 0.6:
        return 2.0
    grown = previous * (1.5 + 1.5 * q)
    return float(min(180.0, round(grown, 1)))


def due_date(interval_days: float, today: date | None = None) -> str:
    today = today or date.today()
    return (today + timedelta(days=round(interval_days))).isoformat()


def expected(user_rating: float, problem_rating: float) -> float:
    return 1.0 / (1.0 + 10 ** ((problem_rating - user_rating) / 400.0))


def update_ratings(user_rating: float, problem_rating: float, q: float) -> tuple[float, float]:
    e = expected(user_rating, problem_rating)
    new_user = user_rating + K_USER * (q - e)
    new_problem = problem_rating - K_PROBLEM * (q - e)
    return round(new_user, 1), round(new_problem, 1)


@dataclass
class ModuleProgress:
    total: int
    solved: int
    avg_quality: float
    assessments_done: set[str]
    assessments_available: set[str]

    @property
    def coverage(self) -> float:
        return self.solved / self.total if self.total else 0.0

    @property
    def score(self) -> float:
        return self.coverage * self.avg_quality

    @property
    def has_content(self) -> bool:
        return self.total > 0

    @property
    def mastered(self) -> bool:
        if not self.has_content:
            return False
        return (
            self.coverage >= MASTERY_COVERAGE
            and self.avg_quality >= MASTERY_QUALITY
            and self.assessments_available <= self.assessments_done
        )

    @property
    def status(self) -> str:
        if not self.has_content:
            return "no-content"
        if self.mastered:
            return "mastered"
        if self.solved:
            return "in-progress"
        return "not-started"

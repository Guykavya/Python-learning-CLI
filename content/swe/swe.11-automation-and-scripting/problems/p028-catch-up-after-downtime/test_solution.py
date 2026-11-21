import json
from datetime import date, datetime, timezone

from solution import missed_days, run_daily

NOW = datetime(2026, 11, 21, 8, 0, tzinfo=timezone.utc)
D = date.fromisoformat


def state_of(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path, day):
    path.write_text(json.dumps({"last_success": day}), encoding="utf-8")


class Recorder:
    def __init__(self, fail_on=()):
        self.calls, self.fail_on = [], set(fail_on)

    def __call__(self, day):
        self.calls.append(day)
        if day in self.fail_on:
            raise ConnectionError(f"source unreachable for {day}")


def test_missed_days_gap():
    assert missed_days(D("2026-11-17"), NOW) == [D("2026-11-18"), D("2026-11-19"), D("2026-11-20"), D("2026-11-21")], \
        "Every day AFTER the last success, up to and INCLUDING today, oldest first."


def test_missed_days_edges():
    assert missed_days(D("2026-11-21"), NOW) == [], "Today already done: nothing to do."
    assert missed_days(D("2026-11-30"), NOW) == [], "A last success in the future (clock trouble) is not a reason to run."
    assert missed_days(None, NOW) == [D("2026-11-21")], "Never succeeded: just today, no invented backlog."
    assert missed_days(D("2026-11-20"), NOW) == [D("2026-11-21")]


def test_missed_days_across_a_month():
    assert missed_days(D("2026-10-30"), datetime(2026, 11, 2, 6, 0)) == [D("2026-10-31"), D("2026-11-01"), D("2026-11-02")], \
        "Use timedelta(days=1), not day + 1 on the number: months end."


def test_first_run_does_today(tmp_path):
    state = tmp_path / "state.json"
    job = Recorder()
    assert run_daily(job, state, NOW) == ([D("2026-11-21")], None)
    assert state_of(state) == {"last_success": "2026-11-21"}, "Save {'last_success': 'YYYY-MM-DD'} after the day succeeds."


def test_catches_up_in_order(tmp_path):
    state = tmp_path / "state.json"
    save_state(state, "2026-11-17")
    job = Recorder()
    done, failed = run_daily(job, state, NOW)
    expected = [D("2026-11-18"), D("2026-11-19"), D("2026-11-20"), D("2026-11-21")]
    assert job.calls == expected, f"Call job(day) once per missed day, oldest first; calls were {job.calls}"
    assert (done, failed) == (expected, None)
    assert state_of(state) == {"last_success": "2026-11-21"}


def test_second_run_is_harmless(tmp_path):
    state = tmp_path / "state.json"
    save_state(state, "2026-11-19")
    run_daily(Recorder(), state, NOW)
    again = Recorder()
    assert run_daily(again, state, NOW) == ([], None)
    assert again.calls == [], "Everything up to today is done: a second run must not call the job."


def test_stops_at_first_failure_and_resumes(tmp_path):
    state = tmp_path / "state.json"
    save_state(state, "2026-11-17")
    job = Recorder(fail_on={D("2026-11-19")})
    done, failed = run_daily(job, state, NOW)
    assert (done, failed) == ([D("2026-11-18")], D("2026-11-19")), f"Return (days done, failed day); got {(done, failed)}"
    assert job.calls == [D("2026-11-18"), D("2026-11-19")], "Stop at the first failure: do not run the 20th and 21st on top of a missing day."
    assert state_of(state) == {"last_success": "2026-11-18"}, "The state keeps the last SUCCESSFUL day (saved right after it)."
    fixed = Recorder()
    assert run_daily(fixed, state, NOW) == ([D("2026-11-19"), D("2026-11-20"), D("2026-11-21")], None)
    assert fixed.calls[0] == D("2026-11-19"), "The next run starts again at the failed day."


def test_progress_is_saved_after_each_day(tmp_path):
    state = tmp_path / "state.json"
    save_state(state, "2026-11-18")
    seen = []

    def job(day):
        seen.append(state_of(state)["last_success"])

    run_daily(job, state, NOW)
    assert seen == ["2026-11-18", "2026-11-19", "2026-11-20"], \
        f"Write the state after EACH successful day, not once at the end; the job saw {seen}"


def test_no_temp_files_left(tmp_path):
    state = tmp_path / "state.json"
    save_state(state, "2026-11-15")
    run_daily(Recorder(), state, NOW)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["state.json"], "Use write_json_atomic; no temp files may remain."

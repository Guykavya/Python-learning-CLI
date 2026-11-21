from datetime import datetime, timedelta

import pytest

from solution import meets_targets, restore_time, worst_case_loss, worst_gap

NIGHTS = [datetime(2026, 11, d, 2, 0) for d in range(1, 10)]


def test_the_chapters_case():
    assert worst_case_loss(NIGHTS, datetime(2026, 11, 9, 15, 30)) == 810.0, \
        "The last backup before 15:30 on the 9th is 02:00 the same day: 13.5 hours = 810 minutes of lost orders."


def test_order_of_backups_does_not_matter():
    shuffled = [NIGHTS[3], NIGHTS[0], NIGHTS[8], NIGHTS[5]]
    assert worst_case_loss(shuffled, datetime(2026, 11, 9, 15, 30)) == 810.0, "Take the LATEST backup that is not after the failure (max), not the first in the list."


def test_a_backup_after_the_failure_does_not_count():
    failure = datetime(2026, 11, 5, 12, 0)
    assert worst_case_loss(NIGHTS, failure) == 600.0, "02:00 on the 5th is 10 hours before; the backup at 02:00 on the 6th is in the future."


def test_backup_exactly_at_failure():
    assert worst_case_loss(NIGHTS, datetime(2026, 11, 3, 2, 0)) == 0.0, "A backup taken at the very moment of failure loses nothing."


def test_loss_across_midnight_and_days():
    assert worst_case_loss([datetime(2026, 11, 1, 23, 0)], datetime(2026, 11, 3, 1, 30)) == 26 * 60 + 30, "Use real time differences, not hour arithmetic."


def test_no_backup_before_the_failure():
    with pytest.raises(ValueError):
        worst_case_loss(NIGHTS, datetime(2026, 10, 31, 12, 0))
    with pytest.raises(ValueError):
        worst_case_loss([], datetime(2026, 11, 1))


def test_worst_gap_is_the_real_rpo_of_the_schedule():
    assert worst_gap(NIGHTS) == 1440.0, "Nightly backups: the worst case is a failure just before the next backup: a full 24 hours."


def test_worst_gap_finds_the_longest_hole():
    times = [datetime(2026, 11, 1, 2), datetime(2026, 11, 2, 2), datetime(2026, 11, 5, 2), datetime(2026, 11, 5, 14)]
    assert worst_gap(list(reversed(times))) == 3 * 1440.0, "A weekend without a backup (3 days) is the real RPO; sort the times before comparing neighbours."


def test_worst_gap_needs_two_backups():
    for times in ([], [datetime(2026, 11, 1)]):
        with pytest.raises(ValueError):
            worst_gap(times)


def test_restore_time():
    assert restore_time(2, 100, 30) == pytest.approx(30 + 2 * 1024 / 100 / 60), "fixed minutes + data volume / speed: 2 GB = 2048 MB at 100 MB/s = 20.48 s."
    assert restore_time(0, 50, 15) == 15, "No data to copy: only the fixed work."
    assert restore_time(500, 100, 20) == pytest.approx(20 + 500 * 1024 / 100 / 60), "A 500 GB database at 100 MB/s needs about 85 minutes of copying alone."


@pytest.mark.parametrize("args", [(1, 0, 5), (1, -1, 5), (-1, 10, 5), (1, 10, -5)])
def test_restore_time_bad_input(args):
    with pytest.raises(ValueError):
        restore_time(*args)


def test_meets_targets():
    assert meets_targets(810, 45, rpo_minutes=60, rto_minutes=60) == {"rpo_ok": False, "rto_ok": True}, \
        "Nightly backups cannot meet a 60-minute RPO, but a 45-minute restore meets a 60-minute RTO."
    assert meets_targets(60, 60, rpo_minutes=60, rto_minutes=60) == {"rpo_ok": True, "rto_ok": True}, "Exactly on target is OK (<=)."
    assert meets_targets(61, 61, 60, 60) == {"rpo_ok": False, "rto_ok": False}


def test_a_backup_every_hour_changes_the_picture():
    hourly = [datetime(2026, 11, 9, 0, 0) + timedelta(hours=h) for h in range(24)]
    assert meets_targets(worst_case_loss(hourly, datetime(2026, 11, 9, 15, 30)), 45, 60, 60)["rpo_ok"] is True, \
        "With hourly backups the loss at 15:30 is 30 minutes: within a 60-minute RPO."

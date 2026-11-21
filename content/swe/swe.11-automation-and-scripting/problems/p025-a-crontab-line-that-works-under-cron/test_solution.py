import pytest

from solution import cron_line

PY, SCRIPT, LOG = "/home/me/venv/bin/python", "/home/me/auto/tidy.py", "/home/me/auto/tidy.log"


def test_full_line():
    line = cron_line("30 2 * * 1-5", PY, SCRIPT, LOG, args=["organize", "/home/me/Downloads"])
    assert line == ("30 2 * * 1-5 cd /home/me/auto && /home/me/venv/bin/python /home/me/auto/tidy.py "
                    "organize /home/me/Downloads >> /home/me/auto/tidy.log 2>&1"), \
        f"Pattern: schedule, cd to the script's folder, &&, python, script, args, '>> log 2>&1'. Got {line!r}"


def test_no_args_and_shortcut_schedule():
    assert cron_line("@reboot", PY, SCRIPT, LOG) == \
        "@reboot cd /home/me/auto && /home/me/venv/bin/python /home/me/auto/tidy.py >> /home/me/auto/tidy.log 2>&1"


def test_extra_spaces_in_the_schedule_are_collapsed():
    assert cron_line("*/15   *  * * *", PY, SCRIPT, LOG).startswith("*/15 * * * * cd /home/me/auto"), \
        "Join the five fields with single spaces."


def test_percent_is_escaped():
    line = cron_line("@daily", "/usr/bin/python3", "/opt/r/report.py", "/var/log/r.log", args=["--stamp=%F", "--fmt=%Y%m"])
    assert "--stamp=\\%F --fmt=\\%Y\\%m" in line, f"Every % in the command becomes \\% (cron reads % as a newline). Got {line!r}"
    assert line.count("%") == line.count("\\%"), "No unescaped % may remain."


@pytest.mark.parametrize("python, script, log", [
    ("python3", SCRIPT, LOG),
    (PY, "tidy.py", LOG),
    (PY, SCRIPT, "logs/tidy.log"),
    (PY, "C:\\tools\\tidy.py", LOG),
])
def test_relative_paths_are_refused(python, script, log):
    with pytest.raises(ValueError, match="absolute"):
        cron_line("0 8 * * *", python, script, log)


@pytest.mark.parametrize("schedule", ["*/15 * * *", "0 8 * * * *", "daily", "", "@daily now"])
def test_bad_schedules_are_refused(schedule):
    with pytest.raises(ValueError):
        cron_line(schedule, PY, SCRIPT, LOG)


def test_spaces_are_refused():
    with pytest.raises(ValueError):
        cron_line("0 8 * * *", PY, "/home/me/my scripts/tidy.py", LOG)
    with pytest.raises(ValueError):
        cron_line("0 8 * * *", PY, SCRIPT, LOG, args=["organize", "/home/me/My Files"])

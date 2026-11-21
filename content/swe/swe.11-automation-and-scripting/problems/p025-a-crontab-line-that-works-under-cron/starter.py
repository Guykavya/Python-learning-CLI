from pathlib import PurePosixPath


def cron_line(schedule, python, script, log, args=()):
    """'<schedule> cd <project> && <python> <script> <args> >> <log> 2>&1', validated, with % escaped."""
    # TODO: validate the schedule, absolute paths, no spaces; build; escape %
    return f"{schedule} {python} {script}"

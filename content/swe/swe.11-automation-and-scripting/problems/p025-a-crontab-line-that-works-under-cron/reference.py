from pathlib import PurePosixPath


def cron_line(schedule, python, script, log, args=()):
    """'<schedule> cd <project> && <python> <script> <args> >> <log> 2>&1', validated, with % escaped."""
    fields = schedule.split()
    if not (len(fields) == 5 or (len(fields) == 1 and fields[0].startswith("@"))):
        raise ValueError(f"a schedule has 5 fields or is one @word: {schedule!r}")
    for name, value in (("python", python), ("script", script), ("log", log)):
        if not PurePosixPath(str(value)).is_absolute():
            raise ValueError(f"{name} must be an absolute path: {value}")
    words = [str(python), str(script)] + [str(a) for a in args]
    for word in words + [str(log)]:
        if " " in word:
            raise ValueError(f"no spaces allowed in a crontab command: {word!r}")
    project = PurePosixPath(str(script)).parent
    command = f"cd {project} && {' '.join(words)} >> {log} 2>&1"
    return " ".join(fields) + " " + command.replace("%", "\\%")

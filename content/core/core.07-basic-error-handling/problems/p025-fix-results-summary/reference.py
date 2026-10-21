def parse_result(line):
    """'name,marks' -> (name, marks). Raise ValueError saying what is wrong with a bad line."""
    parts = line.split(",")
    if len(parts) != 2:
        raise ValueError(f"expected 'name,marks', got {line!r}")
    name, marks_text = parts
    try:
        marks = int(marks_text)
    except ValueError:
        raise ValueError(f"marks must be a whole number, got {marks_text.strip()!r}") from None
    if marks < 0 or marks > 100:
        raise ValueError(f"marks must be from 0 to 100, got {marks}")
    return name.strip(), marks


def summarise(lines):
    """Return (average of valid marks or None, list of 'line N: message' for bad lines)."""
    marks = []
    errors = []
    for number, line in enumerate(lines, start=1):
        try:
            name, value = parse_result(line)
        except ValueError as e:
            errors.append(f"line {number}: {e}")
        else:
            marks.append(value)
    try:
        average = sum(marks) / len(marks)
    except ZeroDivisionError:
        average = None
    return average, errors

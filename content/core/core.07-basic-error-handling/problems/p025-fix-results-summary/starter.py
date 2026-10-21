def parse_result(line):
    """'name,marks' -> (name, marks). Raise ValueError saying what is wrong with a bad line."""
    try:
        name, marks = line.split(",")
        marks = int(marks)
        if marks < 0 or marks > 100:
            raise ValueError("marks out of range")
        return name.strip(), marks
    except:
        raise ValueError("marks must be a whole number")


def summarise(lines):
    """Return (average of valid marks or None, list of 'line N: message' for bad lines)."""
    marks = []
    errors = []
    for number, line in enumerate(lines, start=1):
        try:
            name, value = parse_result(line)
            marks.append(value)
        except Exception:
            pass
    try:
        average = sum(marks) / len(mark)
    except Exception:
        average = None
    return average, errors

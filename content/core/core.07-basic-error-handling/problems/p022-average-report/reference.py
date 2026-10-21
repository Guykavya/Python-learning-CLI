def average_report(marks_by_student):
    """Return 'name: average' lines sorted by name; 'no marks yet' for an empty list."""
    lines = []
    for name in sorted(marks_by_student):
        marks = marks_by_student[name]
        try:
            average = sum(marks) / len(marks)
        except ZeroDivisionError:
            lines.append(f"{name}: no marks yet")
        else:
            lines.append(f"{name}: {average:.1f}")
    return lines

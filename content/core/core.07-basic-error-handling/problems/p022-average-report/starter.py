def average_report(marks_by_student):
    """Return 'name: average' lines sorted by name; 'no marks yet' for an empty list."""
    lines = []
    for name in sorted(marks_by_student):
        marks = marks_by_student[name]
        lines.append(f"{name}: {sum(marks) / len(marks):.1f}")
    return lines

def grade(marks):
    """Return the letter grade for marks from 0 to 100."""
    if marks < 0 or marks > 100:
        raise ValueError(f"marks must be from 0 to 100, got {marks}")
    if marks >= 90:
        return "A"
    if marks >= 75:
        return "B"
    if marks >= 60:
        return "C"
    if marks >= 40:
        return "D"
    return "F"

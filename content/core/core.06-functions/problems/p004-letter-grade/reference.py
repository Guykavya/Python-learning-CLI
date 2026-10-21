def letter_grade(score):
    """Return the letter grade for a score from 0 to 100, or "invalid"."""
    if score < 0 or score > 100:
        return "invalid"
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"

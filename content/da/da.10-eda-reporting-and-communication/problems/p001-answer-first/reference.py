def headline(metric, before, after, period, cause="", unit="%"):
    b, a = round(before, 1), round(after, 1)
    if a == b:
        text = f"{metric} stayed at {b:.1f}{unit} in {period}"
    else:
        verb = "rose" if a > b else "fell"
        text = f"{metric} {verb} from {b:.1f}{unit} to {a:.1f}{unit} in {period}"
    if cause:
        text += f", mainly because {cause}"
    words = len(text.split())
    if words > 40:
        raise ValueError(f"headline is {words} words (more than 40)")
    return text

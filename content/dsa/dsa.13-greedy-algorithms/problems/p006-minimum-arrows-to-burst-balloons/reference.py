def min_arrows(balloons):
    """Fewest vertical arrows that burst every closed interval (x_start, x_end)."""
    arrows = 0
    shot_at = float("-inf")
    for s, e in sorted(balloons, key=lambda b: b[1]):
        if s > shot_at:               # not hit by the last arrow (touching IS hit)
            arrows += 1
            shot_at = e               # shoot as far right as this balloon allows
    return arrows

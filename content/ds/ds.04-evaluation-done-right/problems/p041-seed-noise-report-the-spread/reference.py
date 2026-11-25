import numpy as np


def seed_spread(run, seeds):
    scores = [float(run(s)) for s in seeds]
    if len(scores) < 2:
        raise ValueError("need at least two seeds")
    return {"mean": float(np.mean(scores)), "std": float(np.std(scores, ddof=1)),
            "min": float(min(scores)), "max": float(max(scores)), "n": len(scores)}

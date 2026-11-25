import numpy as np
import pandas as pd
import pandera.pandas as pa


def clean_air(raw, stations=("Hill Road", "Riverside", "Airport")):
    """Return (clean, flags, log, report) for the raw air-quality table (see problem.md)."""
    # TODO: 1. formats  2. duplicates  3. suspects (spike, stuck)  4. validate + quarantine
    #       5. way A (drop) and way B (interpolate <= 3 h, then a humidity line)  6. report text
    raise NotImplementedError

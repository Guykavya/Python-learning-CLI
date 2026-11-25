from dataclasses import dataclass


@dataclass(frozen=True)
class Metric:
    # TODO: the fields are listed in problem.md
    pass


def compute(metric, jobs, start, end):
    """Compute `metric` for the half-open period [start, end)."""
    raise NotImplementedError("filter by the date basis, drop the excluded customers, count numerator and denominator")


METRICS = {}     # TODO: register "jobs_completed" and "completion_rate" here

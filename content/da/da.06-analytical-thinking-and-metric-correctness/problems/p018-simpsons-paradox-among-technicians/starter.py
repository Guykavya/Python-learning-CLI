def completion_by_tech(jobs):
    """Return {"overall": {tech: rate}, "by_type": {job_type: {tech: rate}}}; rate = completed jobs / all jobs of that group."""
    raise NotImplementedError("group by tech, then by job_type and tech; the rate is the share of status == 'completed'")


def paradox(jobs, a, b):
    """True when tech `a` has a higher rate than `b` in every job type both worked on, but a lower overall rate."""
    raise NotImplementedError("compare the per-type rates and the overall rates")

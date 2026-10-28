from functools import reduce


def pipeline(*funcs):
    for step in funcs:
        if not callable(step):
            raise TypeError(f"pipeline step {step!r} is not callable")

    def run(value):
        return reduce(lambda acc, step: step(acc), funcs, value)
    return run

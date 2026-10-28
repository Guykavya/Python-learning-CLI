from functools import reduce


def pipeline(*funcs):
    def run(value):
        return value
    return run

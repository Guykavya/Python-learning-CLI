class CallCounter:
    def __init__(self, func):
        self.func = func
        self.count = 0

    # TODO: make the object callable with __call__

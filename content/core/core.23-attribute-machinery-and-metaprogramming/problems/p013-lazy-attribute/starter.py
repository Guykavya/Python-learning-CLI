class lazy:
    """Decorator: turn a one-argument method into an attribute computed on first read.

    Finish __set_name__ and __get__. Do not add __set__ or __delete__.
    """

    def __init__(self, func):
        self.func = func

    def __set_name__(self, owner, name):
        pass

    def __get__(self, instance, owner=None):
        raise NotImplementedError("compute, cache in instance.__dict__, return")

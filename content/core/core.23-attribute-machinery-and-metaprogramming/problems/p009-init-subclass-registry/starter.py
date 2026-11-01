class Plugin:
    registry = {}
    key = None

    def __init_subclass__(cls, /, key=None, **kwargs):
        # TODO: pass **kwargs on, register cls under key, refuse duplicates
        pass

    @classmethod
    def create(cls, key, *args, **kwargs):
        raise NotImplementedError

class Emitter:
    def __init__(self):
        pass

    def on(self, handler):
        # TODO: register handler, return it
        return handler

    def once(self, handler):
        # TODO: register for one emit only, return it
        return handler

    def off(self, handler):
        # TODO: remove the first registration; True if removed
        return False

    def emit(self, *args, **kwargs):
        # TODO: call every handler, in order, on a snapshot
        pass

    def __len__(self):
        return 0


class EventBus:
    def __init__(self):
        pass

    def on(self, name, handler):
        # TODO: register on the emitter for this event name
        return handler

    def emit(self, name, *args, **kwargs):
        # TODO: call the handlers; return how many were registered
        return 0

    def names(self):
        # TODO: sorted names with at least one handler
        return []

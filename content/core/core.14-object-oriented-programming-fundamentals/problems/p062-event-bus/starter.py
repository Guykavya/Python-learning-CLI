class Event:
    def __init__(self, name, payload=None):
        # TODO
        pass


class EventBus:
    def __init__(self):
        # TODO: where do you keep the listeners of each event name?
        pass

    def subscribe(self, event_name, listener):
        # TODO
        pass

    def unsubscribe(self, event_name, listener):
        # TODO
        pass

    def listeners(self, event_name):
        # TODO
        return []

    def publish(self, event_name, payload=None):
        # TODO
        return 0

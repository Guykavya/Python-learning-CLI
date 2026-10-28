class InvalidTransition(Exception):
    # TODO: store state and action, build the message
    pass


class OrderState:
    name = "?"

    # TODO: pay, ship, deliver, cancel: each raises InvalidTransition(self.name, action)


# TODO: Pending, Paid, Shipped, Delivered, Cancelled


class Order:
    def __init__(self, order_id, initial=None):
        # TODO
        pass

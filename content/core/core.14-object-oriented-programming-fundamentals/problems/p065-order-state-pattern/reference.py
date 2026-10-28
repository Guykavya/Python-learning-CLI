ACTIONS = ("pay", "ship", "deliver", "cancel")


class InvalidTransition(Exception):
    def __init__(self, state, action):
        self.state = state
        self.action = action
        super().__init__(f"cannot {action} an order that is {state}")


class OrderState:
    name = "?"

    def pay(self, order):
        raise InvalidTransition(self.name, "pay")

    def ship(self, order):
        raise InvalidTransition(self.name, "ship")

    def deliver(self, order):
        raise InvalidTransition(self.name, "deliver")

    def cancel(self, order):
        raise InvalidTransition(self.name, "cancel")


class Pending(OrderState):
    name = "pending"

    def pay(self, order):
        return Paid()

    def cancel(self, order):
        return Cancelled()


class Paid(OrderState):
    name = "paid"

    def ship(self, order):
        return Shipped()

    def cancel(self, order):
        order.refunded = True
        return Cancelled()


class Shipped(OrderState):
    name = "shipped"

    def deliver(self, order):
        return Delivered()


class Delivered(OrderState):
    name = "delivered"


class Cancelled(OrderState):
    name = "cancelled"


class Order:
    def __init__(self, order_id, initial=None):
        self.order_id = order_id
        self.refunded = False
        self._state = Pending() if initial is None else initial
        self.history = [self._state.name]

    @property
    def state(self):
        return self._state.name

    @property
    def state_object(self):
        return self._state

    def _apply(self, action):
        method = getattr(self._state, action)
        self._state = method(self)
        self.history.append(self._state.name)

    def pay(self):
        self._apply("pay")

    def ship(self):
        self._apply("ship")

    def deliver(self):
        self._apply("deliver")

    def cancel(self):
        self._apply("cancel")

    def can(self, action):
        if action not in ACTIONS:
            raise ValueError(f"unknown action {action!r}")
        refunded = self.refunded
        try:
            getattr(self._state, action)(self)
        except InvalidTransition:
            return False
        finally:
            self.refunded = refunded  # a trial run must not change the order
        return True

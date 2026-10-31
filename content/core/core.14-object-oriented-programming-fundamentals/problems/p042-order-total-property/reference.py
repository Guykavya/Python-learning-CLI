class Order:
    TAX_RATE = 0.05
    SHIPPING = 40
    FREE_SHIPPING_FROM = 500
    COUPONS = {"WELCOME10": 10, "FEST25": 25, "HALF": 50}

    def __init__(self, customer):
        self.customer = customer
        self._lines = []            # (name, unit_price, qty)
        self._discount_percent = 0
        self._placed = False

    def _check_open(self):
        if self._placed:
            raise RuntimeError("order already placed")

    def add_line(self, name, unit_price, qty=1):
        self._check_open()
        if not isinstance(unit_price, (int, float)) or unit_price < 0:
            raise ValueError(f"unit_price must be a number of at least 0, got {unit_price!r}")
        if not isinstance(qty, int) or qty < 1:
            raise ValueError(f"qty must be a whole number of at least 1, got {qty!r}")
        self._lines.append((name, unit_price, qty))

    @property
    def discount_percent(self):
        return self._discount_percent

    @discount_percent.setter
    def discount_percent(self, value):
        self._check_open()
        if not isinstance(value, (int, float)) or not 0 <= value <= 50:
            raise ValueError(f"discount_percent must be from 0 to 50, got {value!r}")
        self._discount_percent = value

    def apply_coupon(self, code):
        self._check_open()
        self.discount_percent = self.COUPONS[code]      # KeyError for an unknown code

    def place(self):
        self._check_open()
        if not self._lines:
            raise ValueError("cannot place an empty order")
        self._placed = True

    @property
    def placed(self):
        return self._placed

    @property
    def subtotal(self):
        return round(sum(price * qty for _, price, qty in self._lines), 2)

    @property
    def discount(self):
        return round(self.subtotal * self.discount_percent / 100, 2)

    @property
    def tax(self):
        return round((self.subtotal - self.discount) * self.TAX_RATE, 2)

    @property
    def shipping(self):
        if not self._lines or self.subtotal - self.discount >= self.FREE_SHIPPING_FROM:
            return 0
        return self.SHIPPING

    @property
    def total(self):
        return round(self.subtotal - self.discount + self.tax + self.shipping, 2)

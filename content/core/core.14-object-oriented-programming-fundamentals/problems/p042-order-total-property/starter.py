class Order:
    TAX_RATE = 0.05
    SHIPPING = 40
    FREE_SHIPPING_FROM = 500
    COUPONS = {"WELCOME10": 10, "FEST25": 25, "HALF": 50}

    def __init__(self, customer):
        self.customer = customer
        # TODO: lines, discount, placed

    def add_line(self, name, unit_price, qty=1):
        pass

    # TODO: discount_percent property with a setter

    def apply_coupon(self, code):
        pass

    def place(self):
        pass

    # TODO: read-only properties placed, subtotal, discount, tax, shipping, total

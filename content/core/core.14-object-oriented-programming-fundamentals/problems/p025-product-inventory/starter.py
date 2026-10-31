import csv
import io


class Product:
    def __init__(self, sku, name, price, stock=0):
        # TODO: validate price and stock, then store all four values
        pass

    @classmethod
    def from_row(cls, row):
        # TODO: strip the strings, convert price and stock, return cls(...)
        return None


class Inventory:
    def __init__(self):
        pass

    def add(self, product):
        pass

    def get(self, sku):
        return None

    def restock(self, sku, qty):
        pass

    def sell(self, sku, qty):
        return 0

    def low_stock(self, threshold=5):
        return []

    def total_value(self):
        return 0

    @classmethod
    def from_csv(cls, text):
        return cls()

def no_discount(total):
    return total


def percent_off(p):
    def strategy(total):
        return total - total * p / 100
    return strategy


def flat_off(n):
    def strategy(total):
        return max(total - n, 0)
    return strategy


def checkout(items, strategy=no_discount):
    return round(strategy(sum(items)), 2)

from functools import total_ordering

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["clubs", "diamonds", "hearts", "spades"]


class Card:
    def __init__(self, rank, suit):
        # TODO: validate; keep rank and suit; build a sort key
        pass

    # TODO: add @total_ordering above the class, then __eq__, __lt__, __hash__, __repr__

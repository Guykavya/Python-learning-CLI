from functools import total_ordering

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["clubs", "diamonds", "hearts", "spades"]


@total_ordering
class Card:
    def __init__(self, rank, suit):
        if rank not in RANKS:
            raise ValueError(f"bad rank: {rank!r}")
        if suit not in SUITS:
            raise ValueError(f"bad suit: {suit!r}")
        self.rank = rank
        self.suit = suit
        self._key = (RANKS.index(rank), SUITS.index(suit))

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self._key == other._key

    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self._key < other._key

    def __hash__(self):
        return hash(self._key)

    def __repr__(self):
        return f"Card({self.rank!r}, {self.suit!r})"

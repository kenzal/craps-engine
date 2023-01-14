from itertools import combinations_with_replacement,product


class Outcome:
    _d1: int
    _d2: int

    def total(self):
        return self._d1 + self._d2

    def is_hard(self):
        return self._d1 == self._d2

    def __init__(self, d1: int, d2: int):
        if d1 not in range(1, 7) or d2 not in range(1, 7):
            raise ValueError("Dice value must be between 1 and 6")
        self._d1, self._d2 = sorted([d1, d2])

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(sorted([self._d1, self._d2]))

    def __str__(self):
        return "({}, {})".format(*sorted([self._d1, self._d2]))

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, *sorted([self._d1, self._d2]))

    @classmethod
    def get_all(cls):
        return [cls(d1, d2) for d1, d2 in list(product(range(1, 7), repeat=2))]

    @classmethod
    def get_all_unique(cls):
        return [cls(d1, d2) for d1, d2 in list(combinations_with_replacement(range(1, 7), 2))]

    def for_json(self):
        return [self._d1, self._d2]

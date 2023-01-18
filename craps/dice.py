"""
Module: Craps Dice
"""

from itertools import combinations_with_replacement, product


class Outcome:
    """
    A roll of the craps dice.

    Object is immutable and provides a consistent hash for dictionary keys

    Methods
    -------
    is_hard(): bool
        A boolean for if the roll is hard or easy.

        Returns True if the roll is a hard roll (both dice show same numbers).
        Returns False if the roll is an easy roll (both dice show different numbers).
    for_json(): list[int]
        Instance simplified to built-in classes.
    get_all(): list[Outcome]
        A list of all possible combinations of dice.
    get_all(): list[Outcome]
        A list of all unique combinations of dice

        [x, y] is considered the same as [y, x].
    total(): int
        Dice total (2-12).
    """
    _d1: int
    _d2: int

    def __init__(self, first_die: int, second_die: int):
        if first_die not in range(1, 7) or second_die not in range(1, 7):
            raise ValueError("Dice value must be between 1 and 6")
        self._d1, self._d2 = sorted([first_die, second_die])

    def for_json(self):
        """
        Instance simplified to built-in classes.

        :return: list[int]
        """
        return [self._d1, self._d2]

    def is_hard(self):
        """
        A boolean for if the roll is hard or easy.

        Returns True if the roll is a hard roll (both dice show same numbers).
        Returns False if the roll is an easy roll (both dice show different numbers).

        :return: bool
        """
        return self._d1 == self._d2

    @classmethod
    def get_all(cls):
        """
        A list of all possible combinations of dice.

        :return: list[Outcome]
        """
        return [cls(d1, d2) for d1, d2 in list(product(range(1, 7), repeat=2))]

    @classmethod
    def get_all_unique(cls):
        """
        A list of all unique combinations of dice

        [x, y] is considered the same as [y, x]

        :return: list[Outcome]
        """
        return [cls(d1, d2) for d1, d2 in list(combinations_with_replacement(range(1, 7), 2))]

    def total(self):
        """
        Dice total (2-12).

        :return: int
        """
        return self._d1 + self._d2

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple(sorted([self._d1, self._d2])))

    def __str__(self):
        return f"({', '.join(sorted([str(self._d1), str(self._d2)]))})"

    def __repr__(self):
        return f"{self.__class__.__name__}{str(self)}"

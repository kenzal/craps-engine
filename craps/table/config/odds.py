"""
Module: Craps.Table.Config.Odds
"""


class Odds:
    """
    Abstract Odds base class
    """
    _dict = {}

    def __init__(self, odds_dict: dict):
        odds_dict = {int(key): int(val) for key, val in odds_dict.items()}
        if sorted(list(odds_dict.keys())) != sorted(list(self.valid_keys())):
            raise IndexError('Odds should only be defined for all valid keys')
        self._dict = odds_dict

    @classmethod
    def valid_keys(cls):
        """
        A list of valid keys (points) for the concrete class.

        :return: List of points
        :rtype: list[int]
        """
        return []

    @classmethod
    def flat(cls, odds_multiplier: int):
        """
        Odds are the same regardless of point

        :param odds_multiplier: maximum odds for every point
        :type odds_multiplier: int
        :return: Newly Configured Odds Object
        :rtype: Odds
        """

    class UnknownOdds(IndexError):
        """Unknown Odds Error"""

    def __getitem__(self, key: int):
        return self._dict[key]

    def __setitem__(self, key: int, value: int):
        raise TypeError(f"'{self.__class__.__name__}' object does not support item assignment")

    def __hash__(self):
        tuples = tuple(list(self._dict.items()))
        return hash(tuples)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dict})"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)


class StandardOdds(Odds):
    """
    Standard Craps Game Odds Configuration
    """

    @classmethod
    def valid_keys(cls):
        """
        A list of valid keys (points) for the concrete class.

        :return: List of points
        :rtype: list[int]
        """
        return [4, 5, 6, 8, 9, 10]

    @classmethod
    def mirrored345(cls):
        """
        Traditional 3x4x5x odds

        :return: Newly Configured Odds Object
        :rtype: StandardOdds
        """
        return cls({4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3})

    @classmethod
    def flat(cls, odds_multiplier: int):
        """
        Odds are the same regardless of point

        :param odds_multiplier: maximum odds for every point
        :type odds_multiplier: int
        :return: Newly Configured Odds Object
        :rtype: StandardOdds
        """
        return cls({4:  odds_multiplier,
                    5:  odds_multiplier,
                    6:  odds_multiplier,
                    8:  odds_multiplier,
                    9:  odds_multiplier,
                    10: odds_multiplier})

    def for_json(self):
        """
        Odds represented as simple structures

        :return: Constructor Method or Dictionary of Odds
        :rtype: string|dict
        """
        if self == self.mirrored345():
            return "mirrored345()"
        if self == self.flat(self[6]):
            return f"flat({self[6]})"
        return self._dict

    def __repr__(self):
        if self == self.mirrored345():
            return f"{self.__class__.__name__}.mirrored345()"
        if self == self.flat(self[6]):
            return f"{self.__class__.__name__}.flat({self[6]})"
        return super().__repr__()


class CraplessOdds(Odds):
    """
    Crapless Craps Game Odds Configuration
    """

    @classmethod
    def valid_keys(cls):
        """
        A list of valid keys (points) for the concrete class.

        :return: List of points
        :rtype: list[int]
        """
        return [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]

    @classmethod
    def flat(cls, odds_multiplier: int):
        """
        Odds are the same regardless of point

        :param odds_multiplier: maximum odds for every point
        :type odds_multiplier: int
        :return: Newly Configured Odds Object
        :rtype: CraplessOdds
        """
        return cls({key: odds_multiplier for key in range(2, 13) if key != 7})

    def for_json(self):
        """
        Odds represented as simple structures

        :return: Constructor Method or Dictionary of Odds
        :rtype: string|dict
        """
        if self == self.flat(self[6]):
            return f"flat({self[6]})"
        return self._dict

    def __repr__(self):
        if self == self.flat(self[6]):
            return f"{self.__class__.__name__}.flat({self[6]})"
        return super().__repr__()

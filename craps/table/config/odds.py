import json


class Odds:
    _dict = {}

    def __init__(self, odds_dict: dict):
        odds_dict = {int(key): int(val) for key, val in odds_dict.items()}
        if sorted(list(odds_dict.keys())) != sorted(list(self.valid_keys())):
            raise IndexError('Odds should only be defined for all valid keys')
        self._dict = odds_dict

    @classmethod
    def valid_keys(cls):
        return []

    class UnknownOdds(IndexError):
        pass

    @classmethod
    def flat(cls, odds_multiplier: int):
        pass

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

    @classmethod
    def valid_keys(cls):
        return [4, 5, 6, 8, 9, 10]

    @classmethod
    def mirrored345(cls):
        return cls({4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3})

    @classmethod
    def flat(cls, odds_multiplier: int):
        return cls({4: odds_multiplier,
                    5: odds_multiplier,
                    6: odds_multiplier,
                    8: odds_multiplier,
                    9: odds_multiplier,
                    10: odds_multiplier})

    def as_json(self):
        if self == self.mirrored345():
            return json.dumps("mirrored345()")
        if self == self.flat(self[6]):
            return json.dumps(f'flat({self[6]})')
        return json.dumps(self._dict)

    def __repr__(self):
        if self == self.mirrored345():
            return f"{self.__class__.__name__}.mirrored345()"
        if self == self.flat(self[6]):
            return f"{self.__class__.__name__}.flat({self[6]})"
        return super().__repr__()


class CraplessOdds(Odds):

    @classmethod
    def valid_keys(cls):
        return [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]

    @classmethod
    def flat(cls, odds_multiplier: int):
        return cls({key: odds_multiplier for key in range(2, 13) if key != 7})

    def as_json(self):
        if self == self.flat(self[6]):
            return json.dumps(f'flat({self[6]})')
        return json.dumps(self._dict)

    def __repr__(self):
        if self == self.flat(self[6]):
            return f"{self.__class__.__name__}.flat({self[6]})"
        return super().__repr__()

import json


class Odds:
    _dict = {}

    def __init__(self, odds_dict: dict):
        odds_dict = {int(key): val for key, val in odds_dict.items()}
        print(odds_dict)
        if sorted(list(odds_dict.keys())) != sorted(list(self.valid_keys())):
            raise IndexError('Odds should only be defined for all valid keys')
        for val in odds_dict.values():
            if not isinstance(val, int):
                raise TypeError('Odds must be integer')
        self._dict = odds_dict

    @classmethod
    def valid_keys(cls):
        return []

    class UnknownOdds(IndexError):
        pass

    @classmethod
    def flat(cls, x: int):
        pass

    def __getitem__(self, key: int):
        return self._dict[key]

    def __setitem__(self, key: int):
        raise TypeError("'{}' object does not support item assignment".format(self.__class__.__name__))

    def __hash__(self):
        tuples = tuple([(k, v) for k, v in self._dict.items()])
        return hash(tuples)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self._dict)

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
    def flat(cls, x: int):
        return cls({4: x, 5: x, 6: x, 8: x, 9: x, 10: x})

    def as_json(self):
        if self == self.mirrored345():
            return json.dumps("mirrored345()")
        if self == self.flat(self[6]):
            return json.dumps('flat({})'.format(self[6]))
        return json.dumps(self._dict)

    def __repr__(self):
        if self == self.mirrored345():
            return "{0}.mirrored345()".format(self.__class__.__name__)
        if self == self.flat(self[6]):
            return "{0}.flat({1})".format(self.__class__.__name__, self[6])
        return super().__repr__()


class CraplessOdds(Odds):

    @classmethod
    def valid_keys(cls):
        return [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]

    @classmethod
    def flat(cls, x: int):
        return cls({key: x for key in range(2, 13) if key != 7})

    def as_json(self):
        if self == self.flat(self[6]):
            return json.dumps('flat({})'.format(self[6]))
        return json.dumps(self._dict)

    def __repr__(self):
        if self == self.flat(self[6]):
            return "{0}.flat({1})".format(self.__class__.__name__, self[6])
        return super().__repr__()

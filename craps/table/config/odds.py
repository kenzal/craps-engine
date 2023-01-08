class UnknownOdds(IndexError):
    pass


class Odds(tuple):
    @classmethod
    def mirrored345(cls):
        return cls((None, None, None, None, 3, 4, 5, None, 5, 4, 3))

    @classmethod
    def flat(cls, x: int):
        return cls((None, None, None, None, x, x, x, None, x, x, x))

    @classmethod
    def flat_crapsless(cls, x: int):
        return cls((None, None, x, x, x, x, x, None,  x, x, x, x, x))

    def __getitem__(self, key: int):
        if key >= len(self) or super().__getitem__(key) is None:
            raise UnknownOdds('Odds index out of range')
        return super().__getitem__(key)

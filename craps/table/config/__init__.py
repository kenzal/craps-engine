from dataclasses import dataclass
from .odds import Odds, StandardOdds, CraplessOdds
from craps.dice import Outcome as DiceOutcome
import fractions
import json
import JsonEncoder


class InconsistentConfig(Exception):
    pass


@dataclass(frozen=True)
class Config:
    allow_buy_59: bool = False
    allow_put: bool = False
    bet_max: int = None
    bet_min: int = 5
    dont_bar: int = 12
    field_12_pay: int = 3
    field_2_pay: int = 2
    hard_way_max: int = None
    hop_easy_pay_to_one: int = 15
    hop_hard_pay_to_one: int = 30
    hop_max: int = None
    is_crapless: bool = False
    min_buy_lay: int = None
    odds: Odds = StandardOdds.mirrored345()
    odds_max: int = None
    pay_vig_before_buy: bool = False
    pay_vig_before_lay: bool = False
    place_2_12_odds: fractions.Fraction = fractions.Fraction(11, 2)
    place_3_11_odds: fractions.Fraction = fractions.Fraction(11, 4)

    @classmethod
    def from_json(cls, primitive):
        if isinstance(primitive, str):
            primitive = json.loads(primitive)
        if 'place_2_12_odds' in primitive:
            primitive['place_2_12_odds'] = fractions.Fraction(*primitive['place_2_12_odds'])
        if 'place_3_11_odds' in primitive:
            primitive['place_3_11_odds'] = fractions.Fraction(*primitive['place_3_11_odds'])
        if 'odds' in primitive:
            is_crapless = primitive['is_crapless'] if 'is_crapless' in primitive else False
            odds_cls = CraplessOdds if is_crapless else StandardOdds
            if isinstance(primitive['odds'], str):
                primitive['odds'] = eval('{}.{}'.format(odds_cls.__name__, primitive['odds']))
            else:
                primitive['odds'] = {int(key): value for key, value in primitive['odds'].items()}
                primitive['odds'] = eval('{}({})'.format(odds_cls.__name__, primitive['odds']))
        return cls(**primitive)

    def as_json(self):
        diff = self._diff_from_default()
        return json.dumps(diff, cls=JsonEncoder.ComplexEncoder)

    def get_place_odds(self, place: int) -> fractions.Fraction:
        if place in [6, 8]:
            return fractions.Fraction(7, 6)
        if place in [5, 9]:
            return fractions.Fraction(7, 5)
        if place in [4, 10]:
            return fractions.Fraction(9, 5)
        if place in [3, 11] and self.is_crapless:
            return self.place_3_11_odds
        if place in [2, 12] and self.is_crapless:
            return self.place_2_12_odds
        raise ValueError('Invalid place bet')

    @staticmethod
    def get_true_odds(place: int) -> fractions.Fraction:
        ways_to_win = len([out for out in DiceOutcome.get_all() if out.total() == place])
        ways_to_lose = len([out for out in DiceOutcome.get_all() if out.total() == 7])
        return fractions.Fraction(ways_to_lose, ways_to_win)

    def __post_init__(self):
        if self.is_crapless and not isinstance(self.odds, CraplessOdds):
            raise InconsistentConfig('Crapless Config requires CraplessOdds')
        if not self.is_crapless and not isinstance(self.odds, StandardOdds):
            raise InconsistentConfig('Standard Craps requires Standard Odds')
        if self.dont_bar not in [2, 3, 12]:
            raise InconsistentConfig("dont_bar Must Bar a Craps Number")
        if self.bet_min % 5:
            raise InconsistentConfig("bet_min must be multiple of 5")
        if self.bet_max and self.bet_max % 5:
            raise InconsistentConfig("bet_max, if set, must be multiple of 5")
        if self.bet_max and self.bet_max < self.bet_min:
            raise InconsistentConfig("bet_max, if set, must be greater than bet_min")
        for key in [
            'bet_max',
            'bet_min',
            'dont_bar',
            'field_12_pay',
            'field_2_pay',
            'hard_way_max',
            'hop_easy_pay_to_one',
            'hop_hard_pay_to_one',
            'hop_max',
            'min_buy_lay',
            'odds_max',
        ]:
            if getattr(self, key) and getattr(self, key) < 0:
                raise InconsistentConfig('{} Must Be Positive'.format(key))

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__,
                                 ', '.join(['{}={}'.format(key, repr(val)) for key, val in
                                            self._diff_from_default().items()])
                                 )

    def _diff_from_default(self):
        return {attr: getattr(self, attr) for attr in self.__dict__ if
                getattr(self, attr) != getattr(self.__class__(), attr)}

"""
Module: Craps.Table.Config
"""
import fractions
import json
import re
from dataclasses import dataclass

import JsonEncoder
from craps.dice import Outcome as DiceOutcome
from .odds import Odds, StandardOdds, CraplessOdds


class InconsistentConfig(Exception):
    """Inconsistent Configuration"""


@dataclass(frozen=True)
class Config:
    """
    Craps Table Configuration
    """

    # pylint: disable=too-many-instance-attributes
    # Configuration classes always have too many attributes, but they are necessary
    allow_buy_59: bool = False  #: Allow a Buy Bet on 5 and 9
    allow_put: bool = False  #: Allow Put Bets
    bet_max: int = None  #: Bet Maximum
    bet_min: int = 5  #: Bet Minimum
    dont_bar: int = 12  #: Don't Pass and Don't Come Bar Craps
    field_12_pay: int = 3  #: Multiplier for a 12 in the field
    field_2_pay: int = 2  #: Multiplier for a 2 in the field
    hard_way_max: int = None  #: Maximum bet on hard way Bets
    hop_easy_pay_to_one: int = 15  #: Payout Multiplier for easy hops (including 3, 11)
    hop_hard_pay_to_one: int = 30  #: Payout Multiplier for hard hops (including 2, 12)
    hop_max: int = None  #: Maximum wager for hop bet
    is_crapless: bool = False  #: Flag for if the table is crapless craps
    min_buy_lay: int = None  #: Minimum wager for Buy and Lay bets
    odds: Odds = StandardOdds.mirrored345()  #: Maximum Odds for Place/Come/Dont Bets
    odds_max: int = None  #: Maximum Wager on Odds
    pay_vig_before_buy: bool = False  #: Vig required on placing Buy Bet
    pay_vig_before_lay: bool = False  #: Vig required on placing Lay Bet
    #: Place Bet odds for 2 and 12 in Crapless Craps
    place_2_12_odds: fractions.Fraction = fractions.Fraction(11, 2)
    #: Place Bet odds for 3 and 11 in Crapless Craps
    place_3_11_odds: fractions.Fraction = fractions.Fraction(11, 4)

    def get_valid_points(self):
        """
        List of valid points for the current table

        :return: List of valid points
        :rtype: list[int]
        :raise InconsistentConfig: On bad/inconsistent configuration
        """
        return self.odds.valid_keys()

    @classmethod
    def from_json(cls, primitive):
        """
        Build Configuration from a JSON string (or the resulting Dictionary)

        :param primitive: decoded or encoded JSON string
        :type primitive: str|dict
        :return: Config
        """
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
                result = re.search(r"^(?P<method>\w+)\((?P<args>.*)\)$", primitive['odds'])
                if not result:
                    raise InconsistentConfig('Unknown Odds Format')
                if result.group('method') in dir(odds_cls) and \
                        callable(getattr(odds_cls, result.group('method'))):
                    function = getattr(odds_cls, result.group('method'))
                    primitive['odds'] = function(result.group('args'))
                else:
                    raise InconsistentConfig('Unknown Odds Method')
            else:
                primitive['odds'] = odds_cls(dict(primitive['odds'].items()))
        return cls(**primitive)

    def for_json(self):
        """
        Dictionary of Config without Defaults listed

        :return: dict
        """
        return self._diff_from_default()

    def get_place_odds(self, place: int) -> fractions.Fraction:
        """
        Odds for a particular place bet

        :param place: location as integer
        :type place: int
        :return: Odds for place bet
        :rtype: fractions.Fraction
        """
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
        """
        True odds for a particular place

        Used in calculating Odds payouts for Pass/Come/Dont Bets

        :param place: location as int
        :return: true odds
        :rtype: fractions.Fraction
        """
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
                raise InconsistentConfig(f'{key} Must Be Positive')

    def __repr__(self):
        param_string = ', '.join([f'{key}={repr(val)}' for
                                  key, val in self._diff_from_default().items()])
        return f"{self.__class__.__name__}({param_string})"

    def _diff_from_default(self):
        return {attr: getattr(self, attr) for attr in self.__dict__ if
                getattr(self, attr) != getattr(self.__class__(), attr)}

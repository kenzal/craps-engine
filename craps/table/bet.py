from craps.table.puck import Puck
from craps.dice import Outcome as DiceOutcome
import craps.table.config as TableConfig
import typing


class InvalidBet(Exception):
    pass


class Bet:
    wager: int
    odds: int = None
    _puck: Puck
    _table_config: TableConfig
    location: typing.Union[int, None]
    allow_odds: bool = False
    has_vig: bool = False
    can_toggle: bool = False
    single_roll: bool = False
    multi_bet: int = 0

    def __init__(self, wager: int, puck: Puck, table_config: TableConfig, odds: int = None, location=None):
        if wager <= 0:
            raise InvalidBet('Wager must be positive integer')
        if self.multi_bet and wager % self.multi_bet:
            raise InvalidBet('Wager for {} must be multiple of {}'.format(self.__class__.__name__, self.multi_bet))
        self.wager = wager
        self._puck = puck
        self._table_config = table_config
        self.location = location
        if odds:
            if self.allow_odds:
                self.odds = odds
            else:
                raise InvalidBet('Odds not allowed for {} bet'.format(self.__class__.__name__))
        self._check_valid()

    def _check_valid(self):
        pass

    def is_winner(self, outcome: DiceOutcome) -> bool:
        pass

    def is_loser(self, outcome: DiceOutcome) -> bool:
        if self.single_roll:
            return not self.is_winner(outcome)

    def get_payout(self, outcome: DiceOutcome) -> int:
        pass


class PassLine(Bet):
    allow_odds = True

    def move(self, location: int):
        if self.location:
            raise InvalidBet('Can not move {} bet twice.'.format(self.__class__.__name__))
        if location not in self._table_config.odds.valid_keys():
            raise InvalidBet('Illegal location for {} bet'.format(self.__class__.__name__))
        self.location = location


class Put(PassLine):
    def _check_valid(self):
        if not self.location:
            raise InvalidBet('Put bet requires a location')
        if self.location not in self._table_config.odds.valid_keys():
            raise InvalidBet('{} is not a valid location for a Put bet'.format(self.location))


class Come(PassLine):
    pass


class DontPass(PassLine):
    pass


class DontCome(Come, DontPass):
    pass


class Field(Bet):
    single_roll = True

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 4, 9, 10, 11, 12]


class Place(Bet):
    can_toggle = True

    def _check_valid(self):
        if not self.location:
            raise InvalidBet('{0} bet requires a location'.format(self.__class__.__name__))
        if self.location not in self._table_config.odds.valid_keys():
            raise InvalidBet('{1} is not a valid location for a {0} bet'.format(self.__class__.__name__, self.location))


class Buy(Place):
    has_vig = True


class HardWay(Bet):
    can_toggle = True

    def _check_valid(self):
        if not self.location:
            raise InvalidBet('{0} bet requires a location'.format(self.__class__.__name__))
        if self.location not in [4, 6, 8, 10]:
            raise InvalidBet('{1} is not a valid location for a {0} bet'.format(self.__class__.__name__, self.location))

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() == self.location and outcome.is_hard()

    def is_loser(self, outcome: DiceOutcome):
        return outcome.total() == self.location and not outcome.is_hard()


class Prop(Bet):
    single_roll = True


class AnySeven(Prop):
    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() == 7


class AnyCraps(Prop):
    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 12]


class Hop(Prop):
    outcome: DiceOutcome
    single_roll = True

    def __init__(self, wager: int, puck: Puck, table_config: TableConfig, outcome: DiceOutcome):
        self.outcome = outcome
        super().__init__(wager=wager, puck=puck, table_config=table_config, odds=None, location=None)

    def is_winner(self, outcome: DiceOutcome):
        return outcome == self.outcome


class Horn(Prop):
    multi_bet = 4

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]


class HornHigh(Horn):
    multi_bet = 5


class World(Prop):
    multi_bet = 5


class Craps3Way(Prop):
    multi_bet = 3

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 12]


class CnE(Prop):
    multi_bet = 2

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]


class Lay(Bet):
    has_vig = True
    can_toggle = True

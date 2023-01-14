import json

from JsonEncoder import ComplexEncoder
from craps.table.puck import Puck
from craps.dice import Outcome as DiceOutcome
from enum import Enum
import dataclasses
import sys
import craps.table.config as TableConfig
import typing


class BetStatus(Enum):
    ON = 'ON'
    OFF = 'OFF'


class InvalidBet(Exception):
    pass


class BadBetAction(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class BetSignature:
    type: type
    wager: int
    odds: int = None
    placement: typing.Union[None, int, DiceOutcome] = None
    override_puck: typing.Union[BetStatus, None] = None

    def for_json(self):
        return {key: val for key, val in {
            'type': self.type.__name__,
            'wager': self.wager,
            'odds': self.odds,
            'placement': self.placement,
            'override_puck': self.override_puck
        }.items() if val is not None}

class Bet:
    wager: int
    odds: int = None
    _puck: Puck
    _table_config: TableConfig
    location: typing.Union[int, None] = None
    allow_odds: bool = False
    has_vig: bool = False
    can_toggle: bool = False
    single_roll: bool = False
    multi_bet: int = 0
    _override_toggle: typing.Union[BetStatus, None] = None
    can_take_down = True

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
                self.set_odds(odds)
            else:
                raise InvalidBet('Odds not allowed for {} bet'.format(self.__class__.__name__))
        self._check_valid()

    def get_signature(self):
        if self.__class__ == Bet:
            raise TypeError('Cannot create signature of Bet Class')
        return BetSignature(type=self.__class__,
                            wager=self.wager,
                            odds=self.odds,
                            placement=self.location,
                            override_puck=self._override_toggle)

    @classmethod
    def from_signature(cls, signature: BetSignature, puck: Puck, table_config: TableConfig):
        if isinstance(signature, dict):
            if isinstance(signature['type'], str):
                current_module = sys.modules[__name__]
                lower_dict = {a.lower(): a for a in dir(current_module) if a[0:2] != '__'}
                signature['type'] = getattr(current_module, lower_dict[signature['type'].lower()])
            if signature['type'] == Bet or not issubclass(signature['type'], Bet):
                raise InvalidBet(f"{signature['type'].__name__} is not a valid Bet Class")
            signature = BetSignature(**signature)
        if cls == Bet:
            return signature.type.from_signature(signature=signature, puck=puck, table_config=table_config)
        bet = cls(wager=signature.wager,
                  puck=puck,
                  table_config=table_config,
                  odds=signature.odds,
                  location=signature.placement)
        if signature.override_puck is not None:
            bet._override_toggle = signature.override_puck
        return bet

    def _check_valid(self):
        pass

    def max_odds(self) -> int:
        return 0

    def get_vig(self) -> int:
        return int(self.wager * .05) if self.has_vig else 0

    def set_odds(self, odds: int):
        max_odds = self.max_odds()
        if self.allow_odds and 0 < odds <= max_odds:
            self.odds = odds
        elif odds > max_odds:
            raise InvalidBet(f'Odds can not exceed {max_odds} for this bet')
        else:
            raise InvalidBet(f'Odds not allowed for {self.__class__.__name__} bet')

    def remove_odds(self):
        self.odds = 0

    def is_winner(self, outcome: DiceOutcome) -> bool:
        pass

    def is_loser(self, outcome: DiceOutcome) -> bool:
        if self.single_roll:
            return not self.is_winner(outcome)

    def get_payout(self, outcome: DiceOutcome) -> int:
        pass

    def is_on(self) -> bool:
        if self._override_toggle == BetStatus.ON or not self.can_toggle:
            return True
        if self._override_toggle == BetStatus.OFF:
            return False
        return self._puck.is_on()

    def turn_off(self):
        if not self.can_toggle:
            raise BadBetAction(f'Can not turn off {self.__class__.__name__} bet')
        self._override_toggle = BetStatus.OFF

    def turn_on(self):
        self._override_toggle = BetStatus.ON

    def follow_puck(self):
        self._override_toggle = None

    def increase(self, amount: int):
        self.wager += amount

    def for_json(self):
        return self.get_signature()

    def __eq__(self, other):
        return self.__class__ == other.__class__ and dir(self) == dir(other)


class PassLine(Bet):
    allow_odds = True
    can_take_down = False

    def move(self, location: int):
        if self.location:
            raise InvalidBet('Can not move {} bet after point.'.format(self.__class__.__name__))
        if location not in self._table_config.odds.valid_keys():
            raise InvalidBet('Illegal location for {} bet'.format(self.__class__.__name__))
        self.location = location

    def is_loser(self, outcome: DiceOutcome) -> bool:
        if self.location and outcome.total() == 7:
            return True
        if self.location is None and not self._table_config.is_crapless and outcome.total() in [2, 3, 12]:
            return True
        return False

    def is_winner(self, outcome: DiceOutcome) -> bool:
        if self.location and outcome.total() == self.location:
            return True
        if self.location is None and outcome.total() == 7:
            return True
        if self.location is None and not self._table_config.is_crapless and outcome.total() == 11:
            return True
        return False

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        true_odds = self._table_config.get_true_odds(self.location) if self.location else 0
        odds_payout = int(self.odds * true_odds) if self.odds else 0
        return self.wager + odds_payout

    def max_odds(self) -> int:
        return int(self._table_config.odds[self.location] * self.wager)


class Put(PassLine):
    def _check_valid(self):
        if not self.location:
            raise InvalidBet('Put bet requires a location')
        if self.location not in self._table_config.odds.valid_keys():
            raise InvalidBet('{} is not a valid location for a Put bet'.format(self.location))


class Come(PassLine):
    pass


class DontPass(PassLine):
    def _check_valid(self):
        if self._table_config.is_crapless:
            raise InvalidBet(f'{self.__class__.__name__} is not a valid bet for Crapless')

    def is_winner(self, outcome: DiceOutcome) -> bool:
        if self.location and outcome.total() == 7:
            return True
        if self.location is None and outcome.total() in [2, 3, 12] and outcome.total() != self._table_config.dont_bar:
            return True
        return False

    def is_loser(self, outcome: DiceOutcome) -> bool:
        if self.location and outcome.total() == self.location:
            return True
        if self.location is None and outcome.total() in [7, 11]:
            return True
        return False

    def increase(self, amount: int):
        raise InvalidBet("Can not increase contract Don't bets")

    def max_odds(self) -> int:
        pass_odds = self._table_config.get_true_odds(self.location)  # 2/1
        max_win = int(self._table_config.odds[self.location] * self.wager)  # 3 * 5 = 15
        return int(max_win * pass_odds)  # 60 / 2 = 30

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        true_odds = self._table_config.get_true_odds(self.location) if self.location else 0
        odds_payout = int(self.odds / true_odds) if self.odds else 0
        return self.wager + odds_payout


class DontCome(DontPass):
    pass


class Field(Bet):
    single_roll = True

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 4, 9, 10, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        if outcome.total() == 2:
            return self.wager * self._table_config.field_2_pay
        if outcome.total() == 12:
            return self.wager * self._table_config.field_12_pay
        return self.wager


class Place(Bet):
    can_toggle = True

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager * self._table_config.get_place_odds(outcome.total()))

    def is_loser(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == 7

    def is_winner(self, outcome: DiceOutcome) -> bool:
        return self.is_on() and outcome.total() == self.location

    def _check_valid(self):
        if not self.location:
            raise InvalidBet('{0} bet requires a location'.format(self.__class__.__name__))
        if self.location not in self._table_config.odds.valid_keys():
            raise InvalidBet('{1} is not a valid location for a {0} bet'.format(self.__class__.__name__, self.location))


class Buy(Place):
    has_vig = True

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager * self._table_config.get_true_odds(outcome.total())) - self.get_vig()


class Lay(Bet):
    has_vig = True
    _override_toggle = BetStatus.ON
    can_toggle = True

    def is_winner(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == 7

    def is_loser(self, outcome: DiceOutcome) -> bool:
        return self.is_on() and outcome.total() == self.location

    def _check_valid(self):
        if not self.location:
            raise InvalidBet('{0} bet requires a location'.format(self.__class__.__name__))
        if self.location not in self._table_config.odds.valid_keys():
            raise InvalidBet('{1} is not a valid location for a {0} bet'.format(self.__class__.__name__, self.location))

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self._table_config.get_true_odds(self.location)) - self.get_vig()

    def get_vig(self) -> int:
        return int(self.wager / self._table_config.get_true_odds(self.location) * .05) if self.has_vig else 0


class Hardway(Bet):
    can_toggle = True

    def _check_valid(self):
        if not self.location:
            raise InvalidBet('{0} bet requires a location'.format(self.__class__.__name__))
        if self.location not in [4, 6, 8, 10]:
            raise InvalidBet('{1} is not a valid location for a {0} bet'.format(self.__class__.__name__, self.location))

    def is_winner(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == self.location and outcome.is_hard()

    def is_loser(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == self.location and not outcome.is_hard()

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * (7 if outcome.total() in [4, 10] else 9)


class Prop(Bet):
    single_roll = True

    def get_signature(self):
        if self.__class__ == Prop:
            raise TypeError('Cannot create signature of Prop Class')
        return super().get_signature()


class AnySeven(Prop):
    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() == 7

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * 4


class AnyCraps(Prop):
    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * 7


class Hop(Prop):
    outcome: DiceOutcome
    single_roll = True

    def __init__(self, wager: int, puck: Puck, table_config: TableConfig, outcome: DiceOutcome):
        if not isinstance(outcome, DiceOutcome):
            outcome = DiceOutcome(*outcome)
        self.outcome = outcome
        super().__init__(wager=wager, puck=puck, table_config=table_config, odds=None, location=None)

    def is_winner(self, outcome: DiceOutcome):
        return outcome == self.outcome

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * (self._table_config.hop_hard_pay_to_one if outcome.is_hard()
                             else self._table_config.hop_easy_pay_to_one)

    def get_signature(self):
        return BetSignature(type=self.__class__, wager=self.wager, odds=self.odds, placement=self.outcome)

    @classmethod
    def from_signature(cls, signature: BetSignature, puck: Puck, table_config: TableConfig):
        return cls(wager=signature.wager,
                   puck=puck,
                   table_config=table_config,
                   outcome=signature.placement)


class Horn(Prop):
    multi_bet = 4

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self.multi_bet * (self._table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                  else self._table_config.hop_easy_pay_to_one))


class HornHigh(Horn):
    multi_bet = 5

    def _check_valid(self):
        if not self.location:
            raise InvalidBet('{0} bet requires a location'.format(self.__class__.__name__))
        if self.location not in [2, 3, 11, 12]:
            raise InvalidBet('{1} is not a valid location for a {0} bet'.format(self.__class__.__name__, self.location))

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        if outcome.total() == self.location:
            return int(self.wager / self.multi_bet * 2 * (self._table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                          else self._table_config.hop_easy_pay_to_one))
        return int(self.wager / self.multi_bet * (self._table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                  else self._table_config.hop_easy_pay_to_one))


class World(Prop):
    multi_bet = 5

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]

    def is_loser(self, outcome: DiceOutcome):
        return outcome.total() not in [2, 3, 7, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self.multi_bet * (self._table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                  else self._table_config.hop_easy_pay_to_one))


class Craps3Way(Prop):
    multi_bet = 3

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self.multi_bet * (self._table_config.hop_hard_pay_to_one if outcome.is_hard()
                                                  else self._table_config.hop_easy_pay_to_one))


class CE(Prop):
    multi_bet = 2

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        if outcome.total() in [2, 3, 12]:
            return int(self.wager / self.multi_bet * 7)
        return int(self.wager / self.multi_bet * self._table_config.hop_easy_pay_to_one)

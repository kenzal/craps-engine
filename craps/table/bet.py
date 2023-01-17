"""
Module: Craps.Table.Bet
"""
import dataclasses
import sys
import typing
from collections.abc import Iterable
from enum import Enum

import craps.table.config as TableConfig
from craps.dice import Outcome as DiceOutcome
from craps.table.puck import Puck


class BetStatus(Enum):
    """
    Enum for On/Off Bet Status
    """
    ON = 'ON'  #: Bet is On
    OFF = 'OFF'  #: Bet is Off


class InvalidBet(Exception):
    """Invalid Bet Exception"""


class BadBetAction(Exception):
    """
    Bad Bet Action Exception

    Raised when an illegal action is attempted on a bet
    """


@dataclasses.dataclass(frozen=True)
class BetSignature:
    """
    Simple representation of a bet regardless of table/puck
    """
    type: type  #: Type of bet
    wager: int  #: Wager on the bet
    odds: int = None  #: Any fair odds placed on the bet
    placement: typing.Union[None, int, DiceOutcome] = None  #: Where the bet is.
    override_puck: typing.Union[BetStatus, None] = None  #: BetStatus regardless of puck status
    payout: int = None  #: Payout on the bet (used after dice roll for winning bets)

    def for_json(self):
        """
        Table object as primitive types for json encoding

        :return: dict representing table definition
        :rtype: dict
        """
        puck = self.override_puck
        if isinstance(puck, BetStatus):
            puck = puck.value
        return {key: val for key, val in {
            'type':          self.type.__name__,
            'wager':         self.wager,
            'odds':          self.odds,
            'placement':     self.placement,
            'override_puck': puck
        }.items() if val is not None}

    def same_type_and_place(self, other):
        """
        Comparator function to compare type and location of bet

        :param other: Bet to compare two
        :type other: Bet|BetSignature
        :return: Bet is same type and location
        :rtype: bool
        """
        if isinstance(other, Bet):
            return other.get_signature().type == self.type \
                and other.get_signature().placement == self.placement
        return self.type == other.type and self.placement == other.placement


class Bet:
    """
    Abstract Bet Class

    Encapsulates shared functionality
    """
    wager: int  #: Wager on the bet
    odds: int = None  #: Any fair odds placed on the bet
    _puck: Puck
    _table_config: TableConfig
    location: typing.Union[int, None] = None  #: Where the bet is.
    allow_odds: bool = False  #: if fair odds are allowed on the bet
    has_vig: bool = False  #: if a vigorish is required
    can_toggle: bool = False  #: if the bet can be toggled On and Off
    single_roll: bool = False  #: if the bet only exists for a single roll
    multi_bet: int = 0  #: Bet is made of multiple bets if > 0
    _override_toggle: typing.Union[BetStatus, None] = None

    def __init__(self, wager: int, puck: Puck, odds: int = None, location=None):
        """
        Constructor

        :param wager: wager on the bet
        :type wager: int
        :param puck: puck object for the table
        :type puck: Puck
        :param odds: any existing fair odds on the bet
        :type odds: int
        :param location: location of the bet
        :type location: int
        """
        if wager <= 0:
            raise InvalidBet('Wager must be positive integer')
        if self.multi_bet and wager % self.multi_bet:
            raise InvalidBet(
                f'Wager for {self.__class__.__name__} must be multiple of {self.multi_bet}')
        self.wager = wager
        self._puck = puck
        self._table_config = puck.table_config
        self.location = location
        if odds:
            if self.allow_odds:
                self.set_odds(odds)
            else:
                raise InvalidBet(f'Odds not allowed for {self.__class__.__name__} bet')
        self._check_valid()

    def can_remove(self) -> bool:
        """
        Bet can be taken down

        :rtype: bool
        """
        return True

    def can_increase(self) -> bool:
        """
        Bet can be increased

        :rtype: bool
        """
        return True

    def can_decrease(self) -> bool:
        """
        Bet can be taken decreased

        :rtype: bool
        """
        return True

    def return_vig(self) -> int:
        """
        Amount of vigorish returned when taken down

        :rtype: int
        """
        return 0

    def get_signature(self) -> BetSignature:
        """
        Signature of Bet

        :rtype: BetSignature
        :raise TypeError: if attempting to get signature of base class
        """
        if self.__class__ == Bet:
            raise TypeError('Cannot create signature of Bet Class')
        return BetSignature(type=self.__class__,
                            wager=self.wager,
                            odds=self.odds,
                            placement=self.location,
                            override_puck=self._override_toggle)

    @classmethod
    def from_signature(cls, signature: BetSignature, puck: Puck):
        """
        Build a Bet from a BetSignature

        :param signature: Bet Signature
        :type signature: BetSignature
        :param puck: Point Puck on the table
        :type puck: Puck
        :return: net Bet Instance
        :rtype: Bet
        """
        if isinstance(signature, dict):
            if isinstance(signature['type'], str):
                current_module = sys.modules[__name__]
                lower_dict = {a.lower(): a for a in dir(current_module) if a[0:2] != '__'}
                signature['type'] = getattr(current_module, lower_dict[signature['type'].lower()])
            if signature['type'] == Bet or not issubclass(signature['type'], Bet):
                raise InvalidBet(f"{signature['type'].__name__} is not a valid Bet Class")
            signature = BetSignature(**signature)
        if cls == Bet:
            return signature.type.from_signature(signature=signature, puck=puck)
        bet = cls(wager=signature.wager,
                  puck=puck,
                  odds=signature.odds,
                  location=signature.placement)
        if signature.override_puck is not None:
            bet._override_toggle = BetStatus(signature.override_puck)
        return bet

    def _check_valid(self):
        pass

    def max_odds(self) -> int:
        """
        Maximum fair odds allowed on bet

        :rtype: int
        """
        return 0

    def get_vig(self) -> int:
        """
        Amount of vigorish required for bet

        :rtype: int
        """
        return int(self.wager * .05) if self.has_vig else 0

    def set_odds(self, odds: int):
        """
        Set fair odds on the Bet

        :raise InvalidBet: if odds are too much or cannot be placed on bet
        """
        max_odds = self.max_odds()
        if self.allow_odds and 0 < odds <= max_odds:
            self.odds = odds
        elif odds > max_odds:
            raise InvalidBet(f'Odds can not exceed {max_odds} for this bet')
        else:
            raise InvalidBet(f'Odds not allowed for {self.__class__.__name__} bet')

    def remove_odds(self):
        """
        Remove fair odds from bet
        """
        self.odds = 0

    def is_winner(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a winner

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """

    def is_loser(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a loser

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        if self.single_roll:
            return not self.is_winner(outcome)
        return False

    def get_payout(self, outcome: DiceOutcome) -> int:
        """
        Payout for winning bet

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: int
        """

    def is_on(self) -> bool:
        """
        Bet is active

        :rtype: bool
        """
        if self._override_toggle == BetStatus.ON or not self.can_toggle:
            return True
        if self._override_toggle == BetStatus.OFF:
            return False
        return self._puck.is_on()

    def turn_off(self):
        """
        Set bet to inactive

        :raise BadBetAction: on un-toggleable bet
        """
        if not self.can_toggle:
            raise BadBetAction(f'Can not turn off {self.__class__.__name__} bet')
        self._override_toggle = BetStatus.OFF

    def turn_on(self):
        """
        Set bet to active
        """
        self._override_toggle = BetStatus.ON

    def follow_puck(self):
        """
        Set bet activity to follow puck status
        """
        self._override_toggle = None

    def increase(self, amount: int):
        """
        Increase wager by amount

        :param amount: Amount to increase wager by
        :type amount: int
        """
        self.wager += amount

    def for_json(self):
        """
        Bet object as BetSignature for json encoding

        :return: BetSignature representing bet definition
        :rtype: BetSignature
        """
        return self.get_signature()

    def __eq__(self, other):
        if isinstance(other, BetSignature):
            return self.get_signature() == other
        return self.__class__ == other.__class__ and dir(self) == dir(other)

    def same_type_and_place(self, other):
        """
        Comparator function to compare type and location of bet

        :param other: Bet to compare two
        :type other: Bet|BetSignature
        :return: Bet is same type and location
        :rtype: bool
        """
        if isinstance(other, BetSignature):
            return self.get_signature().type == other.type \
                and self.get_signature().placement == other.placement
        return self.__class__ == other.__class__ and self.location == other.location

    def __str__(self):
        return str(self.get_signature())


class PassLine(Bet):
    """Pass Line Bet"""
    allow_odds = True

    def move(self, location: int):
        """
        Assign bet to point

        :param location: where the bet is to be moved
        :type location: int
        :raise BadBetAction: on illegal move request
        """
        if self.location:
            raise BadBetAction(f'Can not move {self.__class__.__name__} bet after point.')
        if location not in self._table_config.get_valid_points():
            raise BadBetAction(f'Illegal location for {self.__class__.__name__} bet')
        self.location = location

    def is_loser(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a Loser

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        if self.location and outcome.total() == 7:
            return True
        if self.location is None and not self._table_config.is_crapless and outcome.total() in [2,
                                                                                                3,
                                                                                                12]:
            return True
        return False

    def is_winner(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a winner

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        if self.location and outcome.total() == self.location:
            return True
        if self.location is None and outcome.total() == 7:
            return True
        if self.location is None and not self._table_config.is_crapless and outcome.total() == 11:
            return True
        return False

    def get_payout(self, outcome: DiceOutcome) -> int:
        """
        Payout for winning bet

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: int
        """
        if not self.is_winner(outcome):
            return 0
        true_odds = self._table_config.get_true_odds(self.location) if self.location else 0
        odds_payout = int(self.odds * true_odds) if self.odds else 0
        return self.wager + odds_payout

    def max_odds(self) -> int:
        """
        Maximum fair odds allowed on bet

        :rtype: int
        """
        return int(self._table_config.odds[self.location] * self.wager)

    def can_remove(self) -> bool:
        """
        Bet can be taken down

        :rtype: bool
        """
        return self.location is None

    def can_decrease(self) -> bool:
        """
        Bet can be taken decreased

        :rtype: bool
        """
        return self.location is None


class Put(PassLine):
    """Put Bet"""
    def _check_valid(self):
        if not self.location:
            raise InvalidBet('Put bet requires a location')
        if self.location not in self._table_config.get_valid_points():
            raise InvalidBet(f'{self.location} is not a valid location for a Put bet')


class Come(PassLine):
    """Come Bet"""


class DontPass(PassLine):
    """Don't Pass Bet"""
    def _check_valid(self):
        if self._table_config.is_crapless:
            raise InvalidBet(f'{self.__class__.__name__} is not a valid bet for Crapless')

    def is_winner(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a winner

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        if self.location and outcome.total() == 7:
            return True
        if self.location is None \
                and outcome.total() in [2, 3, 12] \
                and outcome.total() != self._table_config.dont_bar:
            return True
        return False

    def is_loser(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a Loser

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        if self.location and outcome.total() == self.location:
            return True
        if self.location is None and outcome.total() in [7, 11]:
            return True
        return False

    def increase(self, amount: int):
        """
        Increase wager by amount

        :param amount: Amount to increase wager by
        :type amount: int
        """
        raise InvalidBet("Can not increase contract Don't bets")

    def max_odds(self) -> int:
        """
        Maximum fair odds allowed on bet

        :rtype: int
        """
        pass_odds = self._table_config.get_true_odds(self.location)  # 2/1
        max_win = int(self._table_config.odds[self.location] * self.wager)  # 3 * 5 = 15
        return int(max_win * pass_odds)  # 60 / 2 = 30

    def get_payout(self, outcome: DiceOutcome) -> int:
        """
        Payout for winning bet

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: int
        """
        if not self.is_winner(outcome):
            return 0
        true_odds = self._table_config.get_true_odds(self.location) if self.location else 0
        odds_payout = int(self.odds / true_odds) if self.odds else 0
        return self.wager + odds_payout

    def can_remove(self) -> bool:
        """
        Bet can be taken down

        :rtype: bool
        """
        return True

    def can_increase(self) -> bool:
        """
        Bet can be increased

        :rtype: bool
        """
        return self.location is None

    def can_decrease(self) -> bool:
        """
        Bet can be taken decreased

        :rtype: bool
        """
        return True


class DontCome(DontPass):
    """Don't Come Bet"""


class Field(Bet):
    """Field Bet"""
    single_roll = True  #: if the bet only exists for a single roll

    def is_winner(self, outcome: DiceOutcome):
        """
        Bet is a winner

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        return outcome.total() in [2, 3, 4, 9, 10, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        """
        Payout for winning bet

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: int
        """
        if not self.is_winner(outcome):
            return 0
        if outcome.total() == 2:
            return self.wager * self._table_config.field_2_pay
        if outcome.total() == 12:
            return self.wager * self._table_config.field_12_pay
        return self.wager


class Place(Bet):
    """Place Bet"""
    can_toggle = True

    def get_payout(self, outcome: DiceOutcome) -> int:
        """
        Payout for winning bet

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: int
        """
        if not self.is_winner(outcome):
            return 0
        return int(self.wager * self._table_config.get_place_odds(outcome.total()))

    def is_loser(self, outcome: DiceOutcome):
        """
        Bet is a loser

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        return self.is_on() and outcome.total() == 7

    def is_winner(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a winner

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        return self.is_on() and outcome.total() == self.location

    def _check_valid(self):
        if not self.location:
            raise InvalidBet(f'{self.__class__.__name__} bet requires a location')
        if self.location not in self._table_config.get_valid_points():
            raise InvalidBet(
                '{self.location} is not a valid location for a {self.__class__.__name__} bet')


class Buy(Place):
    """Buy Bet"""
    has_vig = True

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager * self._table_config.get_true_odds(outcome.total())) - self.get_vig()

    def return_vig(self) -> int:
        return self.get_vig() if self._table_config.pay_vig_before_buy else 0


class Lay(Bet):
    """Lay Bet"""
    has_vig = True
    _override_toggle = BetStatus.ON
    can_toggle = True

    def is_winner(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == 7

    def is_loser(self, outcome: DiceOutcome) -> bool:
        return self.is_on() and outcome.total() == self.location

    def _check_valid(self):
        if not self.location:
            raise InvalidBet(f'{self.__class__.__name__} bet requires a location')
        if self.location not in self._table_config.get_valid_points():
            raise InvalidBet(
                f'{self.location} is not a valid location for a {self.__class__.__name__} bet')

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self._table_config.get_true_odds(self.location)) - self.get_vig()

    def get_vig(self) -> int:
        return int(self.wager / self._table_config.get_true_odds(
            self.location) * .05) if self.has_vig else 0

    def return_vig(self) -> int:
        return self.get_vig() if self._table_config.pay_vig_before_lay else 0


class Hardway(Bet):
    """Hardway Bet"""
    can_toggle = True

    def _check_valid(self):
        if not self.location:
            raise InvalidBet(f'{self.__class__.__name__} bet requires a location')
        if self.location not in [4, 6, 8, 10]:
            raise InvalidBet(
                f'{self.location} is not a valid location for a {self.__class__.__name__} bet')

    def is_winner(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == self.location and outcome.is_hard()

    def is_loser(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == self.location and not outcome.is_hard()

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * (7 if outcome.total() in [4, 10] else 9)


class Prop(Bet):
    """Abstract Proposition Bet"""
    single_roll = True

    def get_signature(self):
        if self.__class__ == Prop:
            raise TypeError('Cannot create signature of Prop Class')
        return super().get_signature()


class AnySeven(Prop):
    """Any Seven Bet"""
    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() == 7

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * 4


class AnyCraps(Prop):
    """Any Craps Bet"""
    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * 7


class Hop(Prop):
    """Hop Bet (includes Horn Numbers)"""
    outcome: DiceOutcome
    single_roll = True

    def __init__(self, wager: int, puck: Puck, outcome: DiceOutcome):
        if not isinstance(outcome, DiceOutcome):
            if not isinstance(outcome, Iterable):
                raise InvalidBet("Unknown Hop")
            outcome = DiceOutcome(*outcome)
        self.outcome = outcome
        super().__init__(wager=wager, puck=puck, odds=None, location=None)

    def is_winner(self, outcome: DiceOutcome):
        return outcome == self.outcome

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * (self._table_config.hop_hard_pay_to_one if outcome.is_hard()
                             else self._table_config.hop_easy_pay_to_one)

    def get_signature(self):
        return BetSignature(type=self.__class__, wager=self.wager, odds=self.odds,
                            placement=self.outcome)

    @classmethod
    def from_signature(cls, signature: BetSignature, puck: Puck):
        return cls(wager=signature.wager,
                   puck=puck,
                   outcome=signature.placement)

    def same_type_and_place(self, other):
        if isinstance(other, BetSignature):
            return self.get_signature().type == other.type \
                and self.get_signature().placement == other.placement
        return self.__class__ == other.__class__ and self.outcome == other.outcome


class Horn(Prop):
    """Multi-Bet: Horn Numbers"""
    multi_bet = 4

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self.multi_bet * (
            self._table_config.hop_hard_pay_to_one if outcome.is_hard()
            else self._table_config.hop_easy_pay_to_one))


class HornHigh(Horn):
    """Multi-Bet: Horn Numbers with 1/5 placed on a specific number"""
    multi_bet = 5

    def _check_valid(self):
        if not self.location:
            raise InvalidBet(f'{self.__class__.__name__} bet requires a location')
        if self.location not in [2, 3, 11, 12]:
            raise InvalidBet(
                f'{self.location} is not a valid location for a {self.__class__.__name__} bet')

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        if outcome.total() == self.location:
            return int(self.wager / self.multi_bet * 2 * (
                self._table_config.hop_hard_pay_to_one if outcome.is_hard()
                else self._table_config.hop_easy_pay_to_one))
        return int(self.wager / self.multi_bet * (
            self._table_config.hop_hard_pay_to_one if outcome.is_hard()
            else self._table_config.hop_easy_pay_to_one))


class World(Prop):
    """World Bet: Horn Bet or AnySeven Bet"""
    multi_bet = 5

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]

    def is_loser(self, outcome: DiceOutcome):
        return outcome.total() not in [2, 3, 7, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self.multi_bet * (
            self._table_config.hop_hard_pay_to_one if outcome.is_hard()
            else self._table_config.hop_easy_pay_to_one))


class Craps3Way(Prop):
    """Multi-Bet: 3-Way Craps (Hop the craps numbers)"""
    multi_bet = 3

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self.multi_bet * (
            self._table_config.hop_hard_pay_to_one if outcome.is_hard()
            else self._table_config.hop_easy_pay_to_one))


class CE(Prop):
    "Multi-Bet: Any Craps Or Eleven"
    multi_bet = 2

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        if outcome.total() in [2, 3, 12]:
            return int(self.wager / self.multi_bet * 7)
        return int(self.wager / self.multi_bet * self._table_config.hop_easy_pay_to_one)

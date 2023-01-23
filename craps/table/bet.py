"""
Module: Craps.Table.Bet
"""
import sys
import typing

from craps.bet import BetStatus, InvalidBetException, BadBetActionException, BetSignature, \
    BetInterface, FairOdds, BetPlacement
from craps.dice import Outcome as DiceOutcome
from craps.table.interface import TableInterface


class BetAbstract(BetInterface):
    """
    Abstract Bet Class

    Encapsulates shared functionality
    """
    allow_odds: bool = False  #: if fair odds are allowed on the bet
    has_vig: bool = False  #: if a vigorish is required
    can_toggle: bool = False  #: if the bet can be toggled On and Off
    single_roll: bool = False  #: if the bet only exists for a single roll
    multi_bet: int = 0  #: Bet is made of multiple bets if > 0
    _override_toggle: typing.Optional[BetStatus] = None
    _table: TableInterface

    def __init__(self,
                 wager: int,
                 table: TableInterface,
                 odds: FairOdds = None,
                 placement: BetPlacement = None):
        """
        Constructor

        :param wager: wager on the bet
        :type wager: int
        :param table: Table on which the bet is placed
        :type table: TableInterface
        :param odds: any existing fair odds on the bet
        :type odds: int
        :param placement: location of the bet
        :type placement: DiceOutcome|int|None
        """
        if wager <= 0:
            raise InvalidBetException('Wager must be positive integer')
        if self.multi_bet and wager % self.multi_bet:
            raise InvalidBetException(
                f'Wager for {self.__class__.__name__} must be multiple of {self.multi_bet}')
        self.wager = wager
        self._table = table
        self.placement = placement
        if odds:
            if self.allow_odds:
                self.set_odds(odds)
            else:
                raise InvalidBetException(f'Odds not allowed for {self.__class__.__name__} bet')
        self._check_valid()

    def is_on(self) -> bool:
        """
        Bet is active

        :rtype: bool
        """
        return self._table.point_set()

    def get_type(self) -> str:
        return self.__class__.__name__

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
        if self.__class__ == BetAbstract:
            raise TypeError('Cannot create signature of Bet Class')
        return BetSignature(type=self.__class__,
                            wager=self.wager,
                            odds=self.odds,
                            placement=self.placement,
                            override_puck=self._override_toggle)

    @classmethod
    def from_signature(cls, signature: typing.Union[BetSignature, dict], table: TableInterface):
        """
        Build a Bet from a BetSignature

        :param signature: Bet Signature
        :type signature: BetSignature
        :param table: Table on which the bet is placed
        :type table: TableInterface
        :return: net Bet Instance
        :rtype: BetAbstract
        """
        if isinstance(signature, dict):
            if isinstance(signature['type'], str):
                current_module = sys.modules[__name__]
                lower_dict = {a.lower(): a for a in dir(current_module) if a[0:2] != '__'}
                signature['type'] = getattr(current_module, lower_dict[signature['type'].lower()])
            if signature['type'] == BetAbstract or not issubclass(signature['type'], BetAbstract):
                raise InvalidBetException(f"{signature['type'].__name__} is not a valid Bet Class")
            signature = BetSignature(**signature)
        if cls == BetAbstract:
            return signature.type.from_signature(signature=signature, table=table)
        bet = cls(wager=signature.wager,
                  table=table,
                  odds=signature.odds,
                  placement=signature.placement)
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
            raise InvalidBetException(f'Odds can not exceed {max_odds} for this bet')
        else:
            raise InvalidBetException(f'Odds not allowed for {self.__class__.__name__} bet')

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

    def same_type_and_place(self, other):
        """
        Comparator function to compare type and location of bet

        :param other: Bet to compare two
        :type other: BetInterface
        :return: Bet is same type and location
        :rtype: bool
        """
        if isinstance(other, BetSignature):
            return self.get_signature().type == other.type \
                and self.get_signature().placement == other.placement
        return self.__class__ == other.__class__ and self.placement == other.placement

    def __eq__(self, other):
        if not isinstance(other, BetAbstract):
            raise NotImplemented
        return self.__class__ == other.__class__ \
            and self._table == other._table \
            and self.placement == other.placement

    def __hash__(self):
        return hash((self.__class__, self._table, self.placement))

    def __str__(self):
        return str(self.get_signature())


def ignore_placement_for_compare(cls):
    def eq_comp(self, other):
        if not isinstance(other, BetAbstract):
            raise NotImplemented
        return self.__class__ == other.__class__ and self._table == other._table

    def new_hash(self):
        return hash((self.__class__, self._table, 'Placement Ignored'))

    setattr(cls, '__eq__', eq_comp)
    setattr(cls, '__hash__', new_hash)
    return cls


class PropBetAbstract(BetAbstract):
    """Abstract Proposition Bet"""
    single_roll = True

    def get_signature(self):
        if self.__class__ == PropBetAbstract:
            raise TypeError('Cannot create signature of Prop Class')
        return super().get_signature()


class ToggleableBetAbstract(BetAbstract):
    """Toggleable Bet"""
    _override_toggle: typing.Optional[BetStatus] = None
    can_toggle: bool = True  #: if the bet can be toggled On and Off
    _table: TableInterface

    def is_on(self) -> bool:
        """
        Bet is active

        :rtype: bool
        """
        if self._override_toggle == BetStatus.ON or not self.can_toggle:
            return True
        if self._override_toggle == BetStatus.OFF:
            return False
        return self._table.point_set()

    def turn_off(self):
        """
        Set bet to inactive

        :raise BadBetAction: on un-toggleable bet
        """
        if not self.can_toggle:
            raise BadBetActionException(f'Can not turn off {self.__class__.__name__} bet')
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


class TravelingBetAbstract(BetAbstract):
    """Traveling Bet"""
    placement: BetPlacement = None  #: Where the bet is.
    _table: TableInterface

    def is_set(self) -> bool:
        """
        Bet is set

        :return: Bet is set
        :rtype: bool
        """
        return self.placement is not None

    def move(self, point: int):
        """
        Assign bet to point

        :param point: where the bet is to be moved
        :type point: int
        :raise BadBetAction: on illegal move request
        """
        if self.placement:
            raise BadBetActionException(f'Can not move {self.__class__.__name__} bet after point.')
        if point not in self._table.config.get_valid_points():
            raise BadBetActionException(f'Illegal location for {self.__class__.__name__} bet')
        self.placement = point


class Come(TravelingBetAbstract):
    """Come Bet"""
    allow_odds = True

    def is_loser(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a Loser

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        if self.placement and outcome.total() == 7:
            return True
        if self.placement is None and \
                not self._table.config.is_crapless and \
                outcome.total() in [2, 3, 12]:
            return True
        return False

    def is_winner(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a winner

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        if self.placement and outcome.total() == self.placement:
            return True
        if self.placement is None and outcome.total() == 7:
            return True
        if self.placement is None and not self._table.config.is_crapless and outcome.total() == 11:
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
        true_odds = self._table.config.get_true_odds(self.placement) if self.placement else 0
        odds_payout = int(self.odds * true_odds) if self.odds else 0
        return self.wager + odds_payout

    def max_odds(self) -> int:
        """
        Maximum fair odds allowed on bet

        :rtype: int
        """
        return int(self._table.config.odds[self.placement] * self.wager)

    def can_remove(self) -> bool:
        """
        Bet can be taken down

        :rtype: bool
        """
        return self.placement is None

    def can_decrease(self) -> bool:
        """
        Bet can be taken decreased

        :rtype: bool
        """
        return self.placement is None


class Put(Come):
    """Put Bet"""

    def _check_valid(self):
        if not self.placement:
            raise InvalidBetException('Put bet requires a location')
        if self.placement not in self._table.config.get_valid_points():
            raise InvalidBetException(f'{self.placement} is not a valid location for a Put bet')


@ignore_placement_for_compare
class PassLine(Come):
    """Pass Line Bet"""


class DontCome(TravelingBetAbstract):
    """Don't Come Bet"""
    allow_odds = True

    def _check_valid(self):
        if self._table.config.is_crapless:
            raise InvalidBetException(f'{self.__class__.__name__} is not a valid bet for Crapless')

    def is_winner(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a winner

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        if self.placement and outcome.total() == 7:
            return True
        if self.placement is None \
                and outcome.total() in [2, 3, 12] \
                and outcome.total() != self._table.config.dont_bar:
            return True
        return False

    def is_loser(self, outcome: DiceOutcome) -> bool:
        """
        Bet is a Loser

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: bool
        """
        if self.placement and outcome.total() == self.placement:
            return True
        if self.placement is None and outcome.total() in [7, 11]:
            return True
        return False

    def increase(self, amount: int):
        """
        Increase wager by amount

        :param amount: Amount to increase wager by
        :type amount: int
        """
        raise InvalidBetException("Can not increase contract Don't bets")

    def max_odds(self) -> int:
        """
        Maximum fair odds allowed on bet

        :rtype: int
        """
        pass_odds = self._table.config.get_true_odds(self.placement)  # 2/1
        max_win = int(self._table.config.odds[self.placement] * self.wager)  # 3 * 5 = 15
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
        true_odds = self._table.config.get_true_odds(self.placement) if self.placement else 0
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
        return self.placement is None

    def can_decrease(self) -> bool:
        """
        Bet can be taken decreased

        :rtype: bool
        """
        return True


@ignore_placement_for_compare
class DontPass(DontCome):
    """Don't Pass Bet"""


class Field(BetAbstract):
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
            return self.wager * self._table.config.field_2_pay
        if outcome.total() == 12:
            return self.wager * self._table.config.field_12_pay
        return self.wager


class Place(ToggleableBetAbstract):
    """Place Bet"""

    def get_payout(self, outcome: DiceOutcome) -> int:
        """
        Payout for winning bet

        :param outcome: Roll of the Dice
        :type outcome: Outcome
        :rtype: int
        """
        if not self.is_winner(outcome):
            return 0
        return int(self.wager * self._table.config.get_place_odds(outcome.total()))

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
        return self.is_on() and outcome.total() == self.placement

    def _check_valid(self):
        if not self.placement:
            raise InvalidBetException(f'{self.__class__.__name__} bet requires a location')
        if self.placement not in self._table.config.get_valid_points():
            raise InvalidBetException(
                '{self.placement} is not a valid location for a {self.__class__.__name__} bet')


class Buy(Place):
    """Buy Bet"""
    has_vig = True

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager * self._table.config.get_true_odds(outcome.total())) - self.get_vig()

    def return_vig(self) -> int:
        return self.get_vig() if self._table.config.pay_vig_before_buy else 0


class Lay(ToggleableBetAbstract):
    """Lay Bet"""
    has_vig = True
    _override_toggle = BetStatus.ON

    def is_winner(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == 7

    def is_loser(self, outcome: DiceOutcome) -> bool:
        return self.is_on() and outcome.total() == self.placement

    def _check_valid(self):
        if not self.placement:
            raise InvalidBetException(f'{self.__class__.__name__} bet requires a location')
        if self.placement not in self._table.config.get_valid_points():
            raise InvalidBetException(
                f'{self.placement} is not a valid location for a {self.__class__.__name__} bet')

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self._table.config.get_true_odds(self.placement)) - self.get_vig()

    def get_vig(self) -> int:
        return int(self.wager / self._table.config.get_true_odds(
            self.placement) * .05) if self.has_vig else 0

    def return_vig(self) -> int:
        return self.get_vig() if self._table.config.pay_vig_before_lay else 0


class Hardway(ToggleableBetAbstract):
    """Hardway Bet"""

    def _check_valid(self):
        if not self.placement:
            raise InvalidBetException(f'{self.__class__.__name__} bet requires a location')
        if self.placement not in [4, 6, 8, 10]:
            raise InvalidBetException(
                f'{self.placement} is not a valid location for a {self.__class__.__name__} bet')

    def is_winner(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == self.placement and outcome.is_hard()

    def is_loser(self, outcome: DiceOutcome):
        return self.is_on() and outcome.total() == self.placement and not outcome.is_hard()

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * (7 if outcome.total() in [4, 10] else 9)


class AnySeven(PropBetAbstract):
    """Any Seven Bet"""

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() == 7

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * 4


class AnyCraps(PropBetAbstract):
    """Any Craps Bet"""

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * 7


class Hop(PropBetAbstract):
    """Hop Bet (includes Horn Numbers)"""
    single_roll = True

    def _check_valid(self):
        if not isinstance(self.placement, DiceOutcome):
            if not isinstance(self.placement, list):
                raise InvalidBetException("Unknown Hop")
            self.placement = DiceOutcome(*self.placement)

    def is_winner(self, outcome: DiceOutcome):
        return outcome == self.placement

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * (self._table.config.hop_hard_pay_to_one if outcome.is_hard()
                             else self._table.config.hop_easy_pay_to_one)

    def get_signature(self):
        return BetSignature(type=self.__class__, wager=self.wager, odds=self.odds,
                            placement=self.placement)


class Horn(PropBetAbstract):
    """Multi-Bet: Horn Numbers"""
    multi_bet = 4

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self.multi_bet * (
            self._table.config.hop_hard_pay_to_one if outcome.is_hard()
            else self._table.config.hop_easy_pay_to_one))


class HornHigh(Horn):
    """Multi-Bet: Horn Numbers with 1/5 placed on a specific number"""
    multi_bet = 5

    def _check_valid(self):
        if not self.placement:
            raise InvalidBetException(f'{self.__class__.__name__} bet requires a location')
        if self.placement not in [2, 3, 11, 12]:
            raise InvalidBetException(
                f'{self.placement} is not a valid location for a {self.__class__.__name__} bet')

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        if outcome.total() == self.placement:
            return int(self.wager / self.multi_bet * 2 * (
                self._table.config.hop_hard_pay_to_one if outcome.is_hard()
                else self._table.config.hop_easy_pay_to_one))
        return int(self.wager / self.multi_bet * (
            self._table.config.hop_hard_pay_to_one if outcome.is_hard()
            else self._table.config.hop_easy_pay_to_one))


class World(PropBetAbstract):
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
            self._table.config.hop_hard_pay_to_one if outcome.is_hard()
            else self._table.config.hop_easy_pay_to_one))


class Craps3Way(PropBetAbstract):
    """Multi-Bet: 3-Way Craps (Hop the craps numbers)"""
    multi_bet = 3

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return int(self.wager / self.multi_bet * (
            self._table.config.hop_hard_pay_to_one if outcome.is_hard()
            else self._table.config.hop_easy_pay_to_one))


class CE(PropBetAbstract):
    """Multi-Bet: Any Craps Or Eleven"""
    multi_bet = 2

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() in [2, 3, 11, 12]

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        if outcome.total() in [2, 3, 12]:
            return int(self.wager / self.multi_bet * 7)
        return int(self.wager / self.multi_bet * self._table.config.hop_easy_pay_to_one)

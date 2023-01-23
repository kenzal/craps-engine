"""
Module: Craps.Table.Bet_Abstracts
"""
import sys
import typing
from importlib import import_module

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
                bets_module_name = str(__name__).replace('bet_abstracts', 'bets')
                if bets_module_name not in sys.modules:
                    import_module('.'+bets_module_name, __package__)
                concrete_bets_module = sys.modules[bets_module_name]
                lower_dict = {a.lower(): a for a in dir(concrete_bets_module) if a[0:2] != '__'}
                signature['type'] = getattr(concrete_bets_module, lower_dict[signature['type'].lower()])
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


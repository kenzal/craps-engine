"""
Module: Craps.Table.Bet
"""

from .bet_abstracts import BetAbstract, ignore_placement_for_compare,  \
    ToggleableBetAbstract, TravelingBetAbstract, PropBetAbstract
from ..bet import BetStatus, InvalidBetException, BetSignature
from ..dice import Outcome as DiceOutcome


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


@ignore_placement_for_compare
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


@ignore_placement_for_compare
class AnySeven(PropBetAbstract):
    """Any Seven Bet"""

    def is_winner(self, outcome: DiceOutcome):
        return outcome.total() == 7

    def get_payout(self, outcome: DiceOutcome) -> int:
        if not self.is_winner(outcome):
            return 0
        return self.wager * 4


@ignore_placement_for_compare
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


@ignore_placement_for_compare
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


@ignore_placement_for_compare
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


@ignore_placement_for_compare
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


@ignore_placement_for_compare
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

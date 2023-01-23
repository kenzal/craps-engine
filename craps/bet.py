"""
Module: Bet

Holds definition for Table-Independent Bet Concepts
"""
import dataclasses
import typing
from enum import Enum

from craps.dice import Outcome as DiceOutcome
from craps.table.puck import PuckLocation

BetPlacement = typing.Union[PuckLocation, DiceOutcome, None]
FairOdds = typing.Optional[int]


class BetStatus(Enum):
    """
    Enum for On/Off Bet Status
    """
    ON = 'ON'  #: Bet is On
    OFF = 'OFF'  #: Bet is Off


class InvalidBetException(Exception):
    """Invalid Bet Exception"""


class BadBetActionException(Exception):
    """
    Bad Bet Action Exception

    Raised when an illegal action is attempted on a bet
    """


class BetInterface:
    """Bet Interface"""
    wager: int  #: Wager on the bet
    odds: FairOdds = None  #: Any fair odds placed on the bet
    placement: BetPlacement = None  #: Where the bet is.

    def for_json(self) -> dict:
        """
        Table object as primitive types for json encoding

        :return: dict representing table definition
        :rtype: dict
        """

    def same_type_and_place(self, other) -> bool:
        """
        Comparator function to compare type and location of bet

        :param other: Bet to compare two
        :type other: BetInterface
        :return: Bet is same type and location
        :rtype: bool
        """

    def get_type(self) -> str:
        """
        Type of Bet

        :return: Type of Bet
        :rtype: str
        """


BetList = list[BetInterface]


@dataclasses.dataclass(frozen=True)
class BetSignature(BetInterface):
    """
    Simple representation of a bet regardless of table/puck
    """
    wager: int  #: Wager on the bet
    type: type  #: Type of bet
    odds: FairOdds = None  #: Any fair odds placed on the bet
    placement: BetPlacement = None  #: Where the bet is.
    override_puck: typing.Union[BetStatus, None] = None  #: BetStatus regardless of puck status
    payout: int = None  #: Payout on the bet (used after dice roll for winning bets)

    def get_type(self) -> str:
        """
        Type of Bet

        :return: Type of Bet
        :rtype: str
        """
        return self.type.__name__

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
            'type':          self.get_type(),
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
        if not isinstance(other, BetInterface):
            return False
        return self.get_type() == other.get_type() and self.placement == other.placement


def get_bet_from_list(bet_list: BetList,
                      bet_type: typing.Union[type, str],
                      bet_placement: BetPlacement = None) \
        -> typing.Union[None, BetInterface, BetList]:
    """
    Return matching bet(s) from list

    :param bet_list: List of bets to be filtered
    :type bet_list: list[BetInterface]
    :param bet_type: Type of bet to filter for
    :type bet_type: type|str
    :param bet_placement:
    :type bet_placement: None|int|craps.dice.Outcome
    :return: Any Found Bets
    :rtype: None|Bet|list[Bet]
    """
    found = [existing for existing in bet_list if
             existing.get_type() == (bet_type.__name__ if isinstance(bet_type, type) else bet_type)
             and existing.placement == bet_placement]
    if len(found) == 0:
        return None
    if len(found) == 1:
        return found[0]
    return found

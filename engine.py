"""
Module: Craps Engine

This module functions as the engine for the craps microservice
"""
import copy
import json
import os
import secrets
import textwrap
import typing

import jsonschema

from JsonEncoder import ComplexEncoder
from craps.bet import get_bet_from_set, BetSignature
from craps.dice import Outcome as DiceOutcome
from craps.table import table
from craps.table.bet_abstracts import BetAbstract, TravelingBetAbstract
from craps.table.bets import Come, PassLine
from craps.table.table import Table


class Engine:
    """
    Craps Engine

    Functions as the "Dealers" for the craps. Handles the change of state from one to the next.

    Attributes
    ----------
    hash : None|str
        The hash used to generate the dice roll
    dice_roll : None|DiceOutcome
        The dice outcome once made or specified
    table : table
        The craps table
    instructions : dict
        Set of instructions for the engine to manipulate bets *before* the roll
    """
    hash: str = None  #: The hash used to generate the dice roll
    dice_roll: DiceOutcome = None  #: The dice outcome once made or specified
    table: Table = None  #: The craps table
    #: Set of instructions for the engine to manipulate bets *before* the roll
    instructions: dict = None

    def __init__(self,
                 table: Table = None,
                 instructions=None,
                 hash: typing.Union[str, None] = None,
                 dice: typing.Union[DiceOutcome, list, None] = None):
        """
        Initialize a new engine

        :param table: Craps Table
        :type table: table|dict
        :param instructions: Instruction Set For Dealers to process before the dice roll
        :type instructions: dict
        :param hash: SHA-256 hash string used initialize the dice roller
        :type hash: str
        :param dice: Optional specification for dice roll (used if provided)
        :type dice: Outcome|list|None
        """
        # pylint: disable=redefined-builtin
        # `hash` is appropriate here
        self.hash = hash
        if table is None:
            table = {}
        if dice is not None:
            self.dice_roll = dice if isinstance(dice, DiceOutcome) else DiceOutcome(*dice)
        self.table = table if isinstance(table, Table) else Table(**table)
        if instructions is None:
            instructions = {}
        self.instructions = instructions

    def get_result(self):
        """
        Return the result object containing a summary and the next table state

        :return: dict
        """
        self.roll_dice()
        winners = [bet for bet in self.table.bets if
                   isinstance(bet, BetAbstract) and
                   bet.is_on() and
                   bet.is_winner(self.dice_roll)]
        losers = [bet for bet in self.table.bets if
                  isinstance(bet, BetAbstract) and
                  bet.is_on() and
                  bet.is_loser(self.dice_roll)]
        bets_after_roll = [copy.copy(bet) for bet in self.table.bets if bet not in losers]
        new_puck_location = self.table.puck.location()
        winner_signatures = set()
        for bet in winners:
            sig = bet.get_signature().for_json()
            sig['payout'] = bet.get_payout(self.dice_roll)
            if bet.has_vig:
                sig['vig_paid'] = bet.get_vig()
            winner_signatures.add(BetSignature(**sig))

        dice_total = self.dice_roll.total()

        bets_after_roll = self._get_new_bets(bets_after_roll)
        if self.table.puck.is_off() and dice_total in self.table.get_valid_points():
            new_puck_location = dice_total
        elif self.table.puck.is_on() and dice_total in [7, self.table.puck.location()]:
            new_puck_location = None

        return {
            'table':     {
                'config':         self.table.config,
                'puck_location':  self.table.puck.location(),
                'bets':           self.table.bets,
                'value_on_table': sum(bet.wager for bet in self.table.bets),
                'value_at_risk':  sum(bet.wager for bet in self.table.bets if
                                      isinstance(bet, BetAbstract) and bet.is_on()),
            },
            'hash':      self.hash,
            'winners':   winner_signatures,
            'losers':    losers,
            'returned':  self.table.returned_bets,
            'new_table': {
                'config':        self.table.config,
                'puck_location': new_puck_location,
                'existing_bets': bets_after_roll,
            },
            'summary':   {
                'dice_outcome':             self.dice_roll,
                'total_returned_to_player': sum(
                    bet.wager + bet.return_vig() + (bet.odds if bet.odds else 0) for
                    bet in self.table.returned_bets if isinstance(bet, BetAbstract)),
                'total_winnings_to_player': sum(bet.get_payout(self.dice_roll) for bet in winners),
                'value_of_losers':          sum(bet.wager for bet in losers),
                'value_on_table':           sum(bet.wager for bet in bets_after_roll),
                'value_at_risk':            sum(bet.wager for bet in
                                                bets_after_roll if bet.is_on()),
            }
        }

    def _get_new_bets(self, bets_after_roll):
        """
        Get the bet-list for the new table state

        :param bets_after_roll: List of bets *after* the roll of the current state (losers removed)
        :return: list[Bet] of bets for the next table state (traveling bets moved or removed)
        """
        # pylint: disable=too-many-branches
        # Logic Tree is as simple as I can get it,
        dice_total = self.dice_roll.total()
        new_bets_after_roll = set()
        for bet in bets_after_roll:
            if not isinstance(bet, TravelingBetAbstract):
                new_bets_after_roll.add(bet)
            # All Traveling Bets
            elif bet.placement is None and dice_total in self.table.get_valid_points():
                self._point_set_for_bet(bet, bets_after_roll, new_bets_after_roll)
            elif bet.placement == dice_total:
                self._point_hit_for_bet(bet, bets_after_roll, new_bets_after_roll)
            elif dice_total == 7 and bet.is_winner(self.dice_roll):
                self.table.returned_bets.add(bet)
            else:
                new_bets_after_roll.add(bet)
        return new_bets_after_roll

    def _point_hit_for_bet(self, bet, bets_after_roll, new_bets_after_roll):
        if isinstance(bet, Come) and not isinstance(bet, PassLine):
            found = get_bet_from_set(bet_set=bets_after_roll,
                                     bet_type=Come,
                                     bet_placement=None)
            if not found or found.wager != bet.wager:
                self.table.returned_bets.add(bet)
            else:
                new_bets_after_roll.add(bet)
        else:
            bet.placement = None
            new_bets_after_roll.add(bet)

    def _point_set_for_bet(self, bet, bets_after_roll, new_bets_after_roll):
        dice_total = self.dice_roll.total()
        if isinstance(bet, Come):
            found = get_bet_from_set(bet_set=bets_after_roll,
                                     bet_type=Come,
                                     bet_placement=dice_total)
            if not found or found.wager != bet.wager:
                bet.placement = dice_total
            new_bets_after_roll.add(bet)
        else:
            bet.placement = dice_total
            new_bets_after_roll.add(bet)

    def process_instructions(self):
        """Process the instructions list."""
        self.table.process_instructions(self.instructions)

    def roll_dice(self):
        """Sets dice_roll to a new value if not set."""
        if self.dice_roll:
            return
        self.hash = (self.hash if self.hash else secrets.token_hex(32)).lower()
        for hex_pair in textwrap.wrap(self.hash, 2):
            octal = f"{int(hex_pair, 16):02o}"
            if len(octal) != 2:
                continue
            if 1 <= int(octal[0]) <= 6 and 1 <= int(octal[1]) <= 6:
                self.dice_roll = DiceOutcome(int(octal[0]), int(octal[1]))
                break
        else:
            red_die = int(self.hash[:32], 16) % 6 + 1
            blue_die = int(self.hash[32:], 16) % 6 + 1
            self.dice_roll = DiceOutcome(red_die, blue_die)


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'RequestSchema.json'), encoding='utf-8') as f:
    requestSchema = json.load(f)

with open(os.path.join(__location__, 'sample-request.json'), encoding='utf-8') as f:
    req = json.load(f)


def process_request(request):
    """
    Validate and process a request object

    :param request: request object
    :return: response object
    """
    try:
        jsonschema.validate(instance=request, schema=requestSchema)
    except jsonschema.exceptions.ValidationError as error:
        return {"success": False, "exception": {"type": str(type(error)), "message": str(error)}}
    original = copy.deepcopy(request)
    request = copy.deepcopy(original)
    engine = Engine(**request)
    engine.process_instructions()
    engine.roll_dice()
    return json.loads(json.dumps(engine.get_result(), cls=ComplexEncoder))

"""
Module: Craps Engine

This module functions as the engine for the craps microservice
"""
import copy
import json
import secrets
import textwrap
import typing

import jsonschema

from JsonEncoder import ComplexEncoder
from craps.dice import Outcome as DiceOutcome
from craps.table import Table
from craps.table.bet import Bet, PassLine, Come


def get_bet_from_list(bet_list: list[Bet],
                      bet_type: typing.Union[type, str],
                      bet_placement: typing.Union[int, None, DiceOutcome]):
    found = [existing for existing in bet_list if
             existing.get_signature().type.__name__ == (bet_type.__name__ if
                                                        isinstance(bet_type, type) else
                                                        bet_type)
             and existing.get_signature().placement == bet_placement]
    if len(found) == 0:
        return None
    if len(found) == 1:
        return found[0]
    return found


class Engine:
    hash: str = None
    dice_roll: DiceOutcome = None
    table: Table = None
    instructions: dict = None

    def __init__(self,
                 table: Table = None,
                 instructions=None,
                 hash: typing.Union[str, None] = None,
                 dice: typing.Union[DiceOutcome, list, None] = None):
        # pylint: disable=redefined-builtin
        # `hash` is appropriate here
        self.hash = hash
        if table is None:
            table = {}
        if dice is not None:
            self.dice_roll = dice if isinstance(dice, DiceOutcome) else DiceOutcome(*dice)
        self.table = table if isinstance(table, Table) else Table(**table)
        if instructions is None:
            instructions = []
        self.instructions = instructions

    def get_result(self):
        winners = [bet for bet in self.table.bets if bet.is_on() and bet.is_winner(self.dice_roll)]
        losers = [bet for bet in self.table.bets if bet.is_on() and bet.is_loser(self.dice_roll)]
        bets_after_roll = [copy.copy(bet) for bet in self.table.bets if bet not in losers]
        new_puck_location = self.table.puck.location()
        winner_signatures = []
        for bet in winners:
            sig = bet.get_signature().for_json()
            sig['payout'] = bet.get_payout(self.dice_roll)
            if bet.has_vig:
                sig['vig_payed'] = bet.get_vig()
            winner_signatures.append(sig)

        dice_total = self.dice_roll.total()

        bets_after_roll = self._get_new_bets(bets_after_roll, dice_total)
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
                'value_at_risk':  sum(bet.wager for bet in self.table.bets if bet.is_on()),
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
                    bet in self.table.returned_bets),
                'total_winnings_to_player': sum(bet.get_payout(self.dice_roll) for bet in winners),
                'value_of_losers':          sum(bet.wager for bet in losers),
                'value_on_table':           sum(bet.wager for bet in bets_after_roll),
                'value_at_risk':            sum(bet.wager for bet in
                                                bets_after_roll if bet.is_on()),
            }
        }

    def _get_new_bets(self, bets_after_roll, dice_total):
        # pylint: disable=too-many-branches
        # Logic Tree is as simple as I can get it
        new_bets_after_roll = []
        for bet in bets_after_roll:
            if not isinstance(bet, PassLine):
                new_bets_after_roll.append(bet)
            # All Traveling Bets
            elif bet.location is None and dice_total in self.table.get_valid_points():
                # when point rolls
                if isinstance(bet, Come):
                    found = get_bet_from_list(bet_list=bets_after_roll,
                                              bet_type=Come,
                                              bet_placement=dice_total)
                    if not found or found.wager != bet.wager:
                        bet.location = dice_total
                    new_bets_after_roll.append(bet)
                else:
                    bet.location = dice_total
                    new_bets_after_roll.append(bet)
            elif bet.location == dice_total:
                if isinstance(bet, Come):
                    found = get_bet_from_list(bet_list=bets_after_roll,
                                              bet_type=Come,
                                              bet_placement=None)
                    if not found or found.wager != bet.wager:
                        self.table.returned_bets.append(bet)
                    else:
                        new_bets_after_roll.append(bet)
                else:
                    bet.location = None
                    new_bets_after_roll.append(bet)
            elif dice_total == 7 and bet.is_winner(self.dice_roll):
                self.table.returned_bets.append(bet)
            else:
                new_bets_after_roll.append(bet)
        return new_bets_after_roll

    def process_instructions(self):
        self.table.process_instructions(self.instructions)

    def roll_dice(self):
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


with open('RequestSchema.json', encoding='utf-8') as f:
    requestSchema = json.load(f)

with open('sample-request.json', encoding='utf-8') as f:
    req = json.load(f)


def process_request(request):
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

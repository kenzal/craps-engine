import copy
import json
import secrets
import textwrap
import typing

import jsonschema as jsonschema

from craps.dice import Outcome as DiceOutcome
from craps.table import Table
from craps.table.bet import Buy, Lay


class Engine:
    hash: str = None
    dice_roll: DiceOutcome = None
    table: Table = None
    instructions: dict = None

    def __init__(self,
                 table: Table = None,
                 instructions=None,
                 hash: typing.Union[str, None] = None,
                 dice: typing.Union[DiceOutcome, None] = None):
        self.hash = hash
        if table is None:
            table = {}
        if dice is not None:
            self.dice_roll = DiceOutcome(*dice)
        self.table = table if isinstance(table, Table) else Table(**table)
        if instructions is None:
            instructions = []
        self.instructions = instructions

    def get_result(self):
        winners = [bet for bet in self.table.bets if bet.is_on() and bet.is_winner(self.dice_roll)]
        losers = [bet for bet in self.table.bets if bet.is_on() and bet.is_loser(self.dice_roll)]
        bets_after_roll = [bet for bet in self.table.bets if bet not in losers]
        new_puck_location = self.table.puck.location()
        winner_signatures = []
        for bet in winners:
            sig = bet.get_signature().for_json()
            sig['payout'] = bet.get_payout(self.dice_roll)
            if bet.has_vig:
                sig['vig_payed'] = bet.get_vig()
            winner_signatures.append(sig)

        if self.table.puck.is_off() and self.dice_roll.total() in self.table.config.odds.valid_keys():
            new_puck_location = self.dice_roll.total()
        elif self.table.puck.is_on() and self.dice_roll.total() in [7, self.table.puck.location()]:
            new_puck_location = None
        # TODO: Handle traveling Bets
        return {
            'table':     {
                'config':         self.table.config,
                'puck_location':  self.table.puck.location(),
                'bets':           self.table.bets,
                'value_on_table': sum([bet.wager for bet in self.table.bets]),
                'value_at_risk':  sum([bet.wager for bet in self.table.bets if bet.is_on()]),
            },
            'hash':      self.hash,
            'winners':   winner_signatures,
            'losers':    losers,
            'new_table': {
                'config':        self.table.config,
                'puck_location': new_puck_location,
                'existing_bets': bets_after_roll,
            },
            'summary':   {
                'dice_outcome':             self.dice_roll,
                'total_returned_to_player': sum([bet.wager + bet.return_vig() for bet in self.table.returned_bets]),
                'total_winnings_to_player': sum([bet.get_payout(self.dice_roll) for bet in winners]),
                'value_of_losers':          sum([bet.wager for bet in losers]),
                'value_on_table':           sum([bet.wager for bet in bets_after_roll]),
                'value_at_risk':            sum([bet.wager for bet in bets_after_roll if bet.is_on()]),
            }
        }

    def process_instructions(self):
        self.table.process_instructions(self.instructions)

    def roll_dice(self):
        if self.dice_roll:
            return
        self.hash = (self.hash if self.hash else secrets.token_hex(32)).lower()
        for hex_pair in textwrap.wrap(self.hash, 2):
            octal = "{0:02o}".format(int(hex_pair, 16))
            if len(octal) != 2:
                continue
            if 1 <= int(octal[0]) <= 6 and 1 <= int(octal[1]) <= 6:
                self.dice_roll = DiceOutcome(int(octal[0]), int(octal[1]))
                break
        else:
            d1 = int(self.hash[:32], 16) % 6 + 1
            d2 = int(self.hash[32:], 16) % 6 + 1
            self.dice_roll = DiceOutcome(d1, d2)


def dict_filter(haystack, needles):
    return dict([(i, haystack[i]) for i in haystack if i in set(needles)])


with open('RequestSchema.json') as f:
    requestSchema = json.load(f)

with open('sample-request.json') as f:
    req = json.load(f)


def process_request(request):
    try:
        jsonschema.validate(instance=request, schema=requestSchema)
    except jsonschema.exceptions.ValidationError as e:
        return {"success": False, "exception": {"type": str(type(e)), "message": str(e)}}
    try:
        original = copy.deepcopy(request)
        request = copy.deepcopy(original)
        engine = Engine(**request)
        engine.process_instructions()
        engine.roll_dice()
        return engine.get_result()
    except Exception as e:
        return {"success": False, "exception": {"type": str(type(e)), "message": str(e)}}

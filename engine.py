import copy
import json
import typing

import jsonschema as jsonschema

from craps.table import Table


class Engine:
    def __init__(self,
                 table: Table = None,
                 instructions=None,
                 hash: typing.Union[str, None] = None):
        self.hash = hash
        if table is None:
            table = {}
        self.table = table if isinstance(table, Table) else Table(**table)
        self.orig_table = copy.deepcopy(self.table)
        if instructions is None:
            instructions = []
        self.instructions = instructions

    def get_result(self):
        return {
            'table':     {
                'config':        self.orig_table.config,
                'puck_location': self.orig_table.puck.location(),
                'existing_bets': self.orig_table.bets,
            },
            'hash':      self.hash,
            'winners':   [],
            'losers':    [],
            'new_table': {
                'config':        self.table.config,
                'puck_location': self.table.puck.location(),
                'existing_bets': self.table.bets,
            },
            'summary':   {
                'dice_outcome':    [1, 1],
                'total_returned_to_player': 0,
                'total_winnings_to_player': 0,
                'value_of_losers': 0,
                'value_on_table':  sum([bet.wager for bet in self.table.bets]),
                'value_at_risk':   sum([bet.wager for bet in self.table.bets if bet.is_on()]),
            }
        }


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
        return json.dumps({"success": False, "exception": {"type": str(type(e)), "message": str(e)}})
    try:
        engine = Engine(**request)
        return engine.get_result()
    except Exception as e:
        return json.dumps({"success": False, "exception": {"type": str(type(e)), "message": str(e)}})

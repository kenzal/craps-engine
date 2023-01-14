import craps
from craps.table import Table
import json
import jsonschema as jsonschema
import typing


class Engine:
    def __init__(self,
                 table: Table = None,
                 instructions=None,
                 hash: typing.Union[str, None] = None):
        self.hash = hash
        if table is None:
            table = {}
        self.table = table if isinstance(table, Table) else Table(**table)
        if instructions is None:
            instructions = []
        self.instructions = instructions

    def get_result(self):
        return {
            'table': {
                'config': self.table.config,
                'puck_location': self.table.puck.location(),
                'existing_bets': self.table.bets,
            },
            'hash': self.hash
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

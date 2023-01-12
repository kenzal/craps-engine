import json

from craps.table.bet import Bet, BetSignature
from craps.table.config import Config
from craps.table.puck import Puck


class Table:
    config: Config
    puck: Puck
    bets: list[Bet]

    def __init__(self,
                 config_object: Config,
                 existing_bets: list[BetSignature] = None):
        self.config = config_object
        self.puck = Puck(self.config)
        if existing_bets:
            self.bets = [Bet.from_signature(signature=signature,
                                            table_config=self.config,
                                            puck=self.puck) for signature in existing_bets]

    def get_bet_signatures(self):
        return [bet.get_signature() for bet in self.bets]

    def as_json(self):
        return json.dumps({
            'config_object': self.config,
            'existing_bets': self.get_bet_signatures(),
            'puck_location': self.puck.location(),
        })

    @classmethod
    def from_json_obj(cls,
                      config_object: Config,
                      existing_bets: list[BetSignature] = None,
                      puck_location: int = None):
        table = cls(config_object=config_object, existing_bets=existing_bets)
        table.puck._location = puck_location


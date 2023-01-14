import json
import typing

from craps.table.bet import Bet, BetSignature
from craps.table.config import Config
from craps.table.puck import Puck


class Table:
    config: Config
    puck: Puck
    bets: list[Bet]

    def __init__(self,
                 config: Config = None,
                 puck_location: typing.Union[int, None] = None,
                 existing_bets: list[BetSignature] = None):
        if config is None:
            config = {}
        self.config = config if isinstance(config, Config) else Config.from_json(json.dumps(config))
        self.puck = Puck(self.config)
        if puck_location is not None:
            self.puck.place(puck_location)
        if existing_bets:
            existing_bets = [Bet.from_signature(signature=signature,
                                                table_config=self.config,
                                                puck=self.puck) for signature in existing_bets]
        self.bets = existing_bets if existing_bets else []

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

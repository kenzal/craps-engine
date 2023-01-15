import json
import typing

from craps.table.bet import Bet, BetSignature, PassLine, InvalidBet, Come, DontPass, DontCome
from craps.table.config import Config
from craps.table.puck import Puck


class DuplicateBetException(Exception):
    pass


class ContractBetException(Exception):
    pass


class Table:
    config: Config
    puck: Puck
    bets: list[Bet]
    returned_bets: list[Bet]

    def __init__(self,
                 config: Config = None,
                 puck_location: typing.Union[int, None] = None,
                 existing_bets: list[BetSignature] = None):
        if config is None:
            config = {}
        self.config = config if isinstance(config, Config) else Config.from_json(config)
        self.puck = Puck(self.config)
        if puck_location is not None:
            self.puck.place(puck_location)
        if existing_bets:
            existing_bets = [Bet.from_signature(signature=signature,
                                                table_config=self.config,
                                                puck=self.puck) for signature in existing_bets]
            for i, a in enumerate(existing_bets):
                if any(a.same_type_and_place(b) for b in existing_bets[:i]):
                    raise DuplicateBetException('Duplicate Bets found in existing bets')
        self.bets = existing_bets if existing_bets else []
        self.returned_bets = []

    def get_bet_signatures(self):
        return [bet.get_signature() for bet in self.bets]

    def as_json(self):
        return json.dumps({
            'config_object': self.config,
            'existing_bets': self.get_bet_signatures(),
            'puck_location': self.puck.location(),
        })

    def process_instructions(self, instructions):
        def process_place(bets: list[BetSignature] = None):
            bets = [Bet.from_signature(signature=signature,
                                       table_config=self.config,
                                       puck=self.puck) for signature in bets]
            for bet in bets:
                if bet.odds is not None:
                    raise InvalidBet("Cannot place bet with odds")
                if type(bet) == PassLine:
                    if any(type(existing) == PassLine for existing in self.bets):
                        raise DuplicateBetException("Cannot place additional PassLine bet")
                    if bet.location is not None:
                        raise InvalidBet("Cannot place PassLine bet with point")
                    if self.puck.is_on():
                        raise InvalidBet("Cannon place PassLine bet while point is established")
                if type(bet) == Come:
                    if bet.location is not None:
                        raise InvalidBet("Cannot place Come bet with point")
                    if self.puck.is_off():
                        raise InvalidBet("Cannon place Come bet unless point is established")
                if type(bet) == DontPass:
                    if any(type(existing) == PassLine for existing in self.bets):
                        raise DuplicateBetException("Cannot place additional DontPass bet")
                    if bet.location is not None:
                        raise InvalidBet("Cannot place DontPass bet with point")
                    if self.puck.is_on():
                        raise InvalidBet("Cannon place DontPass bet while point is established")
                if type(bet) == DontCome:
                    if bet.location is not None:
                        raise InvalidBet("Cannot place DontCome bet with point")
                    if self.puck.is_off():
                        raise InvalidBet("Cannon place DontCome bet unless point is established")
                if any(bet.same_type_and_place(existing) for existing in self.bets):
                    raise DuplicateBetException(f"Cannot place additional {bet}")
                self.bets.append(bet)

        def process_retrieve(bets: list[BetSignature] = None):
            bets = [Bet.from_signature(signature=signature,
                                       table_config=self.config,
                                       puck=self.puck) for signature in bets]
            for bet in bets:
                if not bet.can_remove():
                    raise ContractBetException(f"Cannot retrieve contract bet {bet}")
                for existing_bet in self.bets:
                    if bet.same_type_and_place(existing_bet):
                        self.returned_bets.append(existing_bet)
                self.bets = [existing_bet for existing_bet in self.bets if not bet.same_type_and_place(existing_bet)]

        def process_update(bets: list[BetSignature] = None):
            bets = [Bet.from_signature(signature=signature,
                                       table_config=self.config,
                                       puck=self.puck) for signature in bets]
            for bet in bets:
                for existing_bet in self.bets:
                    if bet.same_type_and_place(existing_bet):
                        if bet.wager > existing_bet.wager and not existing_bet.can_increase():
                            raise ContractBetException(f"Cannot increase wager on contract bet {existing_bet}")
                        if bet.wager < existing_bet.wager and not existing_bet.can_decrease():
                            raise ContractBetException(f"Cannot decrease wager on contract bet {existing_bet}")
                        existing_bet.wager = bet.wager

        def process_set_odds(bets: list[BetSignature] = None):
            bets = [Bet.from_signature(signature=signature,
                                       table_config=self.config,
                                       puck=self.puck) for signature in bets]
            for bet in bets:
                for existing_bet in self.bets:
                    if bet.same_type_and_place(existing_bet):
                        existing_bet.set_odds(bet.odds)

        def process_remove_odds(bets: list[BetSignature] = None):
            bets = [Bet.from_signature(signature=signature,
                                       table_config=self.config,
                                       puck=self.puck) for signature in bets]
            for bet in bets:
                for existing_bet in self.bets:
                    if bet.same_type_and_place(existing_bet):
                        existing_bet.remove_odds()

        def process_turn_on(bets: list[BetSignature] = None):
            bets = [Bet.from_signature(signature=signature,
                                       table_config=self.config,
                                       puck=self.puck) for signature in bets]
            for bet in bets:
                for existing_bet in self.bets:
                    if bet.same_type_and_place(existing_bet):
                        existing_bet.turn_on()

        def process_turn_off(bets: list[BetSignature] = None):
            bets = [Bet.from_signature(signature=signature,
                                       table_config=self.config,
                                       puck=self.puck) for signature in bets]
            for bet in bets:
                for existing_bet in self.bets:
                    if bet.same_type_and_place(existing_bet):
                        existing_bet.turn_off()

        def process_follow_puck(bets: list[BetSignature] = None):
            bets = [Bet.from_signature(signature=signature,
                                       table_config=self.config,
                                       puck=self.puck) for signature in bets]
            for bet in bets:
                for existing_bet in self.bets:
                    if bet.same_type_and_place(existing_bet):
                        existing_bet.follow_puck()

        if 'retrieve' in instructions:
            process_retrieve(instructions['retrieve'])
        if 'place' in instructions:
            process_place(instructions['place'])
        if 'update' in instructions:
            process_update(instructions['update'])
        if 'set_odds' in instructions:
            process_set_odds(instructions['set_odds'])
        if 'remove_odds' in instructions:
            process_remove_odds(instructions['remove_odds'])
        if 'turn_on' in instructions:
            process_turn_on(instructions['turn_on'])
        if 'turn_off' in instructions:
            process_turn_off(instructions['turn_off'])
        if 'follow_puck' in instructions:
            process_follow_puck(instructions['follow_puck'])

    @classmethod
    def from_json_obj(cls,
                      config_object: Config,
                      existing_bets: list[BetSignature] = None,
                      puck_location: int = None):
        table = cls(config=config_object, existing_bets=existing_bets)
        table.puck._location = puck_location

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
                                                puck=self.puck) for signature in existing_bets]
            for i, bet_a in enumerate(existing_bets):
                if any(bet_a.same_type_and_place(bet_b) for bet_b in existing_bets[:i]):
                    raise DuplicateBetException('Duplicate Bets found in existing bets')
        self.bets = existing_bets if existing_bets else []
        self.returned_bets = []

    def get_valid_points(self):
        return self.config.get_valid_points()

    def get_bet_signatures(self):
        return [bet.get_signature() for bet in self.bets]

    def as_json(self):
        return json.dumps({
            'config_object': self.config,
            'existing_bets': self.get_bet_signatures(),
            'puck_location': self.puck.location(),
        })

    def _process_place(self, bets: list[BetSignature] = None):
        bets = [Bet.from_signature(signature=signature, puck=self.puck) for signature in bets]
        for bet in bets:
            if bet.odds is not None:
                raise InvalidBet("Cannot place bet with odds")
            if bet.get_signature().type in (PassLine, DontPass):
                if any(existing.get_signature().type == PassLine for existing in self.bets):
                    raise DuplicateBetException(
                        f"Cannot place additional {bet.__class__.__name__} bet")
                if bet.location is not None:
                    raise InvalidBet(f"Cannot place {bet.__class__.__name__} bet with point")
                if self.puck.is_on():
                    raise InvalidBet(
                        f"Cannon place {bet.__class__.__name__} bet while point is established")
            if bet.get_signature().type in (Come, DontCome):
                if bet.location is not None:
                    raise InvalidBet(f"Cannot place {bet.__class__.__name__} bet with point")
                if self.puck.is_off():
                    raise InvalidBet(
                        f"Cannon place {bet.__class__.__name__} bet unless point is established")
            if any(bet.same_type_and_place(existing) for existing in self.bets):
                raise DuplicateBetException(f"Cannot place additional {bet}")
            self.bets.append(bet)

    def _process_retrieve(self, bets: list[BetSignature] = None):
        bets = [Bet.from_signature(signature=signature, puck=self.puck) for signature in bets]
        for bet in bets:
            if not bet.can_remove():
                raise ContractBetException(f"Cannot retrieve contract bet {bet}")
            for existing_bet in self.bets:
                if bet.same_type_and_place(existing_bet):
                    self.returned_bets.append(existing_bet)
            self.bets = [existing_bet for existing_bet in
                         self.bets if not bet.same_type_and_place(existing_bet)]

    def _process_update(self, bets: list[BetSignature] = None):
        bets = [Bet.from_signature(signature=signature, puck=self.puck) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if bet.same_type_and_place(existing_bet):
                    if bet.wager > existing_bet.wager and not existing_bet.can_increase():
                        raise ContractBetException(
                            f"Cannot increase wager on contract bet {existing_bet}")
                    if bet.wager < existing_bet.wager and not existing_bet.can_decrease():
                        raise ContractBetException(
                            f"Cannot decrease wager on contract bet {existing_bet}")
                    existing_bet.wager = bet.wager

    def _process_set_odds(self, bets: list[BetSignature] = None):
        bets = [Bet.from_signature(signature=signature, puck=self.puck) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if bet.same_type_and_place(existing_bet):
                    existing_bet.set_odds(bet.odds)

    def _process_remove_odds(self, bets: list[BetSignature] = None):
        bets = [Bet.from_signature(signature=signature, puck=self.puck) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if bet.same_type_and_place(existing_bet):
                    existing_bet.remove_odds()

    def _process_turn_on(self, bets: list[BetSignature] = None):
        bets = [Bet.from_signature(signature=signature, puck=self.puck) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if bet.same_type_and_place(existing_bet):
                    existing_bet.turn_on()

    def _process_turn_off(self, bets: list[BetSignature] = None):
        bets = [Bet.from_signature(signature=signature, puck=self.puck) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if bet.same_type_and_place(existing_bet):
                    existing_bet.turn_off()

    def _process_follow_puck(self, bets: list[BetSignature] = None):
        bets = [Bet.from_signature(signature=signature, puck=self.puck) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if bet.same_type_and_place(existing_bet):
                    existing_bet.follow_puck()

    def process_instructions(self, instructions):
        if 'retrieve' in instructions:
            self._process_retrieve(instructions['retrieve'])
        if 'place' in instructions:
            self._process_place(instructions['place'])
        if 'update' in instructions:
            self._process_update(instructions['update'])
        if 'set_odds' in instructions:
            self._process_set_odds(instructions['set_odds'])
        if 'remove_odds' in instructions:
            self._process_remove_odds(instructions['remove_odds'])
        if 'turn_on' in instructions:
            self._process_turn_on(instructions['turn_on'])
        if 'turn_off' in instructions:
            self._process_turn_off(instructions['turn_off'])
        if 'follow_puck' in instructions:
            self._process_follow_puck(instructions['follow_puck'])

    @classmethod
    def from_json_obj(cls,
                      config_object: Config,
                      existing_bets: list[BetSignature] = None,
                      puck_location: int = None):
        table = cls(config=config_object, existing_bets=existing_bets)
        if puck_location:
            table.puck.place(puck_location)
        else:
            table.puck.remove()

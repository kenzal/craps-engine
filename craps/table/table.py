from . import DuplicateBetException, ContractBetException
from .bet_abstracts import BetAbstract, ToggleableBetAbstract
from .bets import PassLine, DontPass, Come, DontCome
from .config import Config
from .interface import TableInterface
from .puck import Puck, PuckLocation
from ..bet import InvalidBetException, BetSignature, BadBetActionException, BetSet


class Table(TableInterface):
    """
    Craps Table Class

    Holds all information about a given table, including the table configuration,
    the puck information, and all existing bets on the table (on or off).
    """
    config: Config  #: Table Configuration (rules)
    puck: Puck  #: The Point Puck on the table
    bets: BetSet  #: List of all bets on the table
    returned_bets: BetSet  #: List of all bets returned to the player

    def __init__(self,
                 config: Config = None,
                 puck_location: PuckLocation = None,
                 existing_bets: BetSet = None):
        """
        Constructor

        :param config: Optional Table Configuration (rules)
        :type config: Config
        :param puck_location: Optional Location of the Point Puck
        :type puck_location: None|int
        :param existing_bets: Optional List of Existing Bets
        :type existing_bets: list[BetSignature]
        """
        if config is None:
            config = {}
        self.config = config if isinstance(config, Config) else Config.from_json(config)
        self.puck = Puck(self.config)
        if puck_location is not None:
            self.puck.place(puck_location)
        if existing_bets:
            existing_bets = set(BetAbstract.from_signature(signature=signature, table=self) for
                                signature in existing_bets
                                if isinstance(signature, (dict, BetSignature)))
        self.bets = existing_bets if existing_bets else set()
        self.returned_bets = set()

    def get_valid_points(self):
        """
        List of valid points for the current table

        :return: Valid Points for Table
        :rtype: list[int]
        """
        return self.config.get_valid_points()

    def get_bet_signatures(self):
        """
        List of all bets as signatures

        :return: All Bet Signatures
        :rtype: list[BetSignature]
        """
        return [bet.get_signature() if isinstance(bet, BetAbstract) else bet for bet in self.bets]

    def for_json(self):
        """
        Table object as primitive types for json encoding

        :return: dict representing table definition
        :rtype: dict
        """
        return {
            'config_object': self.config,
            'existing_bets': self.get_bet_signatures(),
            'puck_location': self.puck.location(),
        }

    def _process_place(self, bets: list[BetSignature] = None):
        bets = [BetAbstract.from_signature(signature=signature, table=self) for signature in bets]
        for bet in bets:
            if bet.odds is not None:
                raise InvalidBetException("Cannot place bet with odds")
            if bet.get_signature().type in (PassLine, DontPass):
                if any(existing.get_signature().type == PassLine
                       for existing in self.bets if isinstance(existing, BetAbstract)):
                    raise DuplicateBetException(
                        f"Cannot place additional {bet.__class__.__name__} bet")
                if bet.placement is not None:
                    raise InvalidBetException(
                        f"Cannot place {bet.__class__.__name__} bet with point")
                if self.puck.is_on():
                    raise InvalidBetException(
                        f"Cannon place {bet.__class__.__name__} bet while point is established")
            if bet.get_signature().type in (Come, DontCome):
                if bet.placement is not None:
                    raise InvalidBetException(
                        f"Cannot place {bet.__class__.__name__} bet with point")
                if self.puck.is_off():
                    raise InvalidBetException(
                        f"Cannon place {bet.__class__.__name__} bet unless point is established")
            if any(bet.same_type_and_place(existing) for existing in self.bets):
                raise DuplicateBetException(f"Cannot place additional {bet}")
            self.bets.add(bet)

    def _process_retrieve(self, bets: list[BetSignature] = None):
        bets = set(BetAbstract.from_signature(signature=signature, table=self) for signature in bets)
        for bet in bets:
            if not bet.can_remove():
                raise ContractBetException(f"Cannot retrieve contract bet {bet}")
            for existing_bet in self.bets:
                if bet.same_type_and_place(existing_bet):
                    self.returned_bets.add(existing_bet)
            self.bets.remove(bet)

    def _process_update(self, bets: list[BetSignature] = None):
        bets = [BetAbstract.from_signature(signature=signature, table=self) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if not isinstance(existing_bet, BetAbstract):
                    if isinstance(existing_bet, (dict, BetSignature)):
                        existing_bet = BetAbstract.from_signature(signature=existing_bet,
                                                                  table=self)
                    else:
                        raise InvalidBetException
                if bet.same_type_and_place(existing_bet):
                    if bet.wager > existing_bet.wager and not existing_bet.can_increase():
                        raise ContractBetException(
                            f"Cannot increase wager on contract bet {existing_bet}")
                    if bet.wager < existing_bet.wager and not existing_bet.can_decrease():
                        raise ContractBetException(
                            f"Cannot decrease wager on contract bet {existing_bet}")
                    existing_bet.wager = bet.wager

    def _process_set_odds(self, bets: list[BetSignature] = None):
        bets = [BetAbstract.from_signature(signature=signature, table=self) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if not isinstance(existing_bet, BetAbstract):
                    if isinstance(existing_bet, (dict, BetSignature)):
                        existing_bet = BetAbstract.from_signature(signature=existing_bet,
                                                                  table=self)
                    else:
                        raise InvalidBetException
                if bet.same_type_and_place(existing_bet):
                    existing_bet.set_odds(bet.odds)

    def _process_remove_odds(self, bets: list[BetSignature] = None):
        bets = [BetAbstract.from_signature(signature=signature, table=self) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if not isinstance(existing_bet, BetAbstract):
                    if isinstance(existing_bet, (dict, BetSignature)):
                        existing_bet = BetAbstract.from_signature(signature=existing_bet,
                                                                  table=self)
                    else:
                        raise InvalidBetException
                if bet.same_type_and_place(existing_bet):
                    existing_bet.remove_odds()

    def _process_turn_on(self, bets: list[BetSignature] = None):
        bets = [BetAbstract.from_signature(signature=signature, table=self) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if not isinstance(existing_bet, BetAbstract):
                    if isinstance(existing_bet, (dict, BetSignature)):
                        existing_bet = BetAbstract.from_signature(signature=existing_bet,
                                                                  table=self)
                    else:
                        raise InvalidBetException
                if not isinstance(existing_bet, ToggleableBetAbstract):
                    raise BadBetActionException
                if bet.same_type_and_place(existing_bet):
                    existing_bet.turn_on()

    def _process_turn_off(self, bets: list[BetSignature] = None):
        bets = [BetAbstract.from_signature(signature=signature, table=self) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if isinstance(existing_bet, (dict, BetSignature)):
                    existing_bet = BetAbstract.from_signature(signature=existing_bet, table=self)
                if not isinstance(existing_bet, BetAbstract):
                    raise InvalidBetException
                if not isinstance(existing_bet, ToggleableBetAbstract):
                    raise BadBetActionException
                if bet.same_type_and_place(existing_bet):
                    existing_bet.turn_off()

    def _process_follow_puck(self, bets: list[BetSignature] = None):
        bets = [BetAbstract.from_signature(signature=signature, table=self) for signature in bets]
        for bet in bets:
            for existing_bet in self.bets:
                if not isinstance(existing_bet, BetAbstract):
                    if isinstance(existing_bet, (dict, BetSignature)):
                        existing_bet = BetAbstract.from_signature(signature=existing_bet,
                                                                  table=self)
                    else:
                        raise InvalidBetException
                if not isinstance(existing_bet, ToggleableBetAbstract):
                    raise BadBetActionException
                if bet.same_type_and_place(existing_bet):
                    existing_bet.follow_puck()

    def process_instructions(self, instructions):
        """
        Process the dictionary of instruction lists

        :param instructions: Dictionary of instruction lists
        :type instructions: dict
        """
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
        """
        Build table from decoded JSON string

        :param config_object:
        :type config_object: dict|None
        :param existing_bets:
        :type existing_bets: list[BetSignature]
        :param puck_location:
        :type puck_location: None|int
        :return: New Table Object
        :rtype: Table
        """
        table = cls(config=config_object, existing_bets=existing_bets)
        if puck_location:
            table.puck.place(puck_location)
        else:
            table.puck.remove()
